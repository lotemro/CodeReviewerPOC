import hashlib
import uuid
import json
import asyncio
from typing import Optional, Tuple
from app.db.repository import ScanRepository
from app.db.models import ScanCreate, ScanInDB, ScanStatus, ScanResponse
from app.reviewer.engine import ReviewerEngine
from app.orchestration.concurrency import ConcurrencyController

class ScanOrchestrator:
    def __init__(
        self, 
        repository: ScanRepository, 
        engine: ReviewerEngine, 
        concurrency_controller: ConcurrencyController
    ):
        self.repository = repository
        self.engine = engine
        self.concurrency_controller = concurrency_controller

    def _calculate_hash(self, content: str) -> str:
        return hashlib.sha256(content.encode()).hexdigest()

    async def request_scan(self, code: str) -> Tuple[ScanResponse, bool]:
        """
        Processes a scan request. 
        Returns (ScanResponse, is_new_scan).
        """
        file_hash = self._calculate_hash(code)
        
        # 1. Check Cache
        cached_scan = await self.repository.get_completed_scan_by_hash(file_hash)
        if cached_scan:
            return ScanResponse(
                id=cached_scan.id,
                status=ScanStatus.COMPLETED,
                results=json.loads(cached_scan.results_json) if cached_scan.results_json else None
            ), False

        # 2. Check Capacity (Atomic-like reservation)
        if not self.concurrency_controller.try_acquire():
            # In a real async app, we'd want to be careful about the race between 
            # try_acquire and the actual background task starting.
            # For this POC, we'll acquire it BEFORE creating the pending record.
            raise CapacityReachedException("Maximum parallel scans reached")

        # 3. Reserve Slot
        await self.concurrency_controller.acquire()
        
        # 4. Create Pending Record
        scan_id = str(uuid.uuid4())
        scan_create = ScanCreate(id=scan_id, file_hash=file_hash, status=ScanStatus.PENDING)
        await self.repository.create_scan(scan_create)

        # 5. Launch Background Task
        # We don't await this, as it's an async background task
        asyncio.create_task(self._run_scan_background(scan_id, code))

        return ScanResponse(id=scan_id, status=ScanStatus.PENDING), True

    async def _run_scan_background(self, scan_id: str, code: str):
        # Background tasks need their own DB connection to avoid closure by request scope
        import aiosqlite
        from aiosqlite import connect
        from app.core.config import settings

        async with connect(settings.DB_PATH) as db:
            db.row_factory = aiosqlite.Row
            repo = ScanRepository(db)
            try:
                await repo.update_scan_status(scan_id, ScanStatus.RUNNING)

                results = await self.engine.review_code(code)

                await repo.update_scan_status(
                    scan_id, 
                    ScanStatus.COMPLETED, 
                    results_json=json.dumps(results)
                )
            except Exception as e:
                await repo.update_scan_status(
                    scan_id, 
                    ScanStatus.FAILED, 
                    error_message=str(e)
                )
            finally:
                self.concurrency_controller.release()

    async def get_scan_result(self, scan_id: str) -> Optional[ScanResponse]:
        scan = await self.repository.get_scan_by_id(scan_id)
        if not scan:
            return None
        
        results = None
        if scan.results_json:
            results = json.loads(scan.results_json)
            
        return ScanResponse(
            id=scan.id,
            status=scan.status,
            results=results,
            error_message=scan.error_message
        )

class CapacityReachedException(Exception):
    pass
