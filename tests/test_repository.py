import pytest
import aiosqlite
import asyncio
from app.db.database import init_db
from app.db.repository import ScanRepository
from app.db.models import ScanCreate, ScanStatus
from app.core.config import settings

@pytest.fixture
async def test_db():
    # Use an in-memory database for testing
    db = await aiosqlite.connect(":memory:")
    db.row_factory = aiosqlite.Row
    await db.execute("""
        CREATE TABLE scans (
            id TEXT PRIMARY KEY,
            file_hash TEXT NOT NULL,
            status TEXT NOT NULL,
            results_json TEXT,
            error_message TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    yield db
    await db.close()

@pytest.mark.asyncio
async def test_create_and_get_scan(test_db):
    repo = ScanRepository(test_db)
    scan_data = ScanCreate(id="test-id", file_hash="hash-123")
    
    created = await repo.create_scan(scan_data)
    assert created.id == "test-id"
    assert created.status == ScanStatus.PENDING
    
    fetched = await repo.get_scan_by_id("test-id")
    assert fetched is not None
    assert fetched.file_hash == "hash-123"

@pytest.mark.asyncio
async def test_update_status(test_db):
    repo = ScanRepository(test_db)
    await repo.create_scan(ScanCreate(id="test-id", file_hash="hash-123"))
    
    await repo.update_scan_status("test-id", ScanStatus.COMPLETED, results_json='{"pass": true}')
    
    updated = await repo.get_scan_by_id("test-id")
    assert updated.status == ScanStatus.COMPLETED
    assert updated.results_json == '{"pass": true}'

@pytest.mark.asyncio
async def test_get_by_hash(test_db):
    repo = ScanRepository(test_db)
    await repo.create_scan(ScanCreate(id="id-1", file_hash="hash-123", status=ScanStatus.COMPLETED))
    
    cached = await repo.get_completed_scan_by_hash("hash-123")
    assert cached is not None
    assert cached.id == "id-1"

@pytest.mark.asyncio
async def test_recovery(test_db):
    repo = ScanRepository(test_db)
    await repo.create_scan(ScanCreate(id="pending", file_hash="h1", status=ScanStatus.PENDING))
    await repo.create_scan(ScanCreate(id="running", file_hash="h2", status=ScanStatus.RUNNING))
    
    await repo.mark_pending_and_running_as_failed()
    
    s1 = await repo.get_scan_by_id("pending")
    s2 = await repo.get_scan_by_id("running")
    assert s1.status == ScanStatus.FAILED
    assert s2.status == ScanStatus.FAILED
