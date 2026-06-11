import pytest
from unittest.mock import AsyncMock, MagicMock
from app.orchestration.orchestrator import ScanOrchestrator, CapacityReachedException
from app.orchestration.concurrency import ConcurrencyController
from app.db.repository import ScanRepository
from app.reviewer.engine import ReviewerEngine
from app.db.models import ScanStatus, ScanInDB
from datetime import datetime

@pytest.fixture
def mock_repo():
    return AsyncMock(spec=ScanRepository)

@pytest.fixture
def mock_engine():
    return AsyncMock(spec=ReviewerEngine)

@pytest.fixture
def concurrency_controller():
    return ConcurrencyController(max_concurrent=1)

@pytest.mark.asyncio
async def test_request_scan_cache_hit(mock_repo, mock_engine, concurrency_controller):
    orchestrator = ScanOrchestrator(mock_repo, mock_engine, concurrency_controller)
    
    mock_repo.get_completed_scan_by_hash.return_value = ScanInDB(
        id="cached-id",
        file_hash="hash",
        status=ScanStatus.COMPLETED,
        results_json='{"rule": true}',
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    
    response, is_new = await orchestrator.request_scan("code")
    
    assert response.id == "cached-id"
    assert response.status == ScanStatus.COMPLETED
    assert is_new is False
    assert mock_engine.review_code.call_count == 0

@pytest.mark.asyncio
async def test_request_scan_capacity_reached(mock_repo, mock_engine, concurrency_controller):
    orchestrator = ScanOrchestrator(mock_repo, mock_engine, concurrency_controller)
    mock_repo.get_completed_scan_by_hash.return_value = None
    
    # Manually lock the semaphore
    await concurrency_controller.acquire()
    
    with pytest.raises(CapacityReachedException):
        await orchestrator.request_scan("code")

@pytest.mark.asyncio
async def test_request_scan_success(mock_repo, mock_engine, concurrency_controller):
    orchestrator = ScanOrchestrator(mock_repo, mock_engine, concurrency_controller)
    mock_repo.get_completed_scan_by_hash.return_value = None
    
    response, is_new = await orchestrator.request_scan("code")
    
    assert response.status == ScanStatus.PENDING
    assert is_new is True
    assert mock_repo.create_scan.call_count == 1
