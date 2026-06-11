import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.db.database import get_db, init_db
from app.api.routes import get_orchestrator
from unittest.mock import AsyncMock, MagicMock
import aiosqlite
import io
import os
from app.core.config import settings

# Override DB for testing
settings.DB_PATH = "test_api.db"

@pytest.fixture(autouse=True)
async def setup_db():
    await init_db()
    yield
    if os.path.exists(settings.DB_PATH):
        os.remove(settings.DB_PATH)

@pytest.fixture
def client():
    # Use lifespan context for initialization
    with TestClient(app) as c:
        yield c

def test_request_scan_invalid_extension(client):
    file_content = b"print('hello')"
    file = io.BytesIO(file_content)
    response = client.post("/scans", files={"file": ("test.txt", file, "text/plain")})
    
    assert response.status_code == 400
    assert "Only .py files are supported" in response.json()["detail"]

def test_get_scan_not_found(client):
    response = client.get("/scans/non-existent-id")
    assert response.status_code == 404
