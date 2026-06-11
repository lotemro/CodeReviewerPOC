import pytest
import io
import os
import asyncio
from fastapi.testclient import TestClient
from app.main import app
from app.db.database import init_db
from app.core.config import settings
from unittest.mock import patch, AsyncMock
from app.api.routes import get_db, get_orchestrator
from app.db.repository import ScanRepository
from app.orchestration.orchestrator import ScanOrchestrator
import aiosqlite

# Override DB for testing
settings.DB_PATH = "test_e2e.db"

@pytest.fixture(autouse=True)
async def setup_db():
    await init_db()
    yield
    # No immediate deletion here to allow background tasks to finish if needed
    # but for tests we want a clean slate

@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c

@pytest.mark.asyncio
async def test_e2e_full_flow(client):
    with patch("app.api.routes.llm_client.generate", new_callable=AsyncMock) as mock_gen:
        mock_gen.side_effect = ["TRUE", "FALSE"]
        
        code = "def hello():\n    \"\"\"Docstring\"\"\"\n    print('hello')"
        file = io.BytesIO(code.encode("utf-8"))
        response = client.post("/scans", files={"file": ("test.py", file, "text/x-python")})
        
        assert response.status_code == 202
        scan_id = response.json()["id"]
        
        # Poll for completion to avoid "closed database" race in background task
        # during TestClient teardown
        for _ in range(10):
            await asyncio.sleep(0.5)
            response = client.get(f"/scans/{scan_id}")
            if response.json()["status"] == "COMPLETED":
                break
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "COMPLETED"
        assert data["results"]["meaningful_variables"] is True
        assert data["results"]["docstring_logic"] is False

@pytest.mark.asyncio
async def test_e2e_cache_hit(client):
    with patch("app.api.routes.llm_client.generate", new_callable=AsyncMock) as mock_gen:
        mock_gen.side_effect = ["TRUE", "TRUE"]
        
        code = "x = 1"
        file1 = io.BytesIO(code.encode("utf-8"))
        resp1 = client.post("/scans", files={"file": ("test1.py", file1, "text/x-python")})
        assert resp1.status_code == 202
        scan_id = resp1.json()["id"]

        # Wait for completion
        for _ in range(10):
            await asyncio.sleep(0.5)
            if client.get(f"/scans/{scan_id}").json()["status"] == "COMPLETED":
                break
        
        # Second scan (same code)
        file2 = io.BytesIO(code.encode("utf-8"))
        resp2 = client.post("/scans", files={"file": ("test2.py", file2, "text/x-python")})
        
        assert resp2.status_code == 200 # Cache hit
        assert resp2.json()["status"] == "COMPLETED"
        assert resp2.json()["id"] == scan_id

@pytest.mark.asyncio
async def test_e2e_concurrency_limit(client):
    from app.api.routes import concurrency_controller
    # Reset semaphore for clean test
    concurrency_controller.semaphore = asyncio.Semaphore(2)
    
    with patch("app.api.routes.llm_client.generate", new_callable=AsyncMock) as mock_gen:
        async def slow_gen(*args):
            await asyncio.sleep(2) # Longer sleep to ensure overlap
            return "TRUE"
        mock_gen.side_effect = slow_gen
        
        code1 = "a = 1"
        code2 = "b = 1"
        code3 = "c = 1"
        
        # Launch requests
        r1 = client.post("/scans", files={"file": ("r1.py", io.BytesIO(code1.encode()), "text/x-python")})
        r2 = client.post("/scans", files={"file": ("r2.py", io.BytesIO(code2.encode()), "text/x-python")})
        
        assert r1.status_code == 202
        assert r2.status_code == 202
        
        # Third one should fail immediately
        r3 = client.post("/scans", files={"file": ("r3.py", io.BytesIO(code3.encode()), "text/x-python")})
        assert r3.status_code == 503
        
        # Cleanup: wait for slow tasks to finish to avoid database closed errors
        await asyncio.sleep(3)
