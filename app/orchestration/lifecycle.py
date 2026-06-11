import asyncio
import logging
from datetime import datetime
from app.db.repository import ScanRepository
from app.core.config import settings

logger = logging.getLogger(__name__)

async def run_recovery(repository: ScanRepository):
    """Marks all PENDING and RUNNING scans as FAILED on startup."""
    logger.info("Running startup recovery...")
    await repository.mark_pending_and_running_as_failed()

async def cleanup_loop():
    """Background task to delete scans older than SCAN_TTL_HOURS."""
    import aiosqlite
    while True:
        try:
            logger.info(f"Running cleanup task (TTL: {settings.SCAN_TTL_HOURS}h)...")
            async with aiosqlite.connect(settings.DB_PATH) as db:
                repository = ScanRepository(db)
                await repository.delete_old_scans(settings.SCAN_TTL_HOURS)
        except Exception as e:
            logger.error(f"Error in cleanup loop: {e}")
        
        # Sleep for 1 hour before next cleanup
        await asyncio.sleep(3600)
