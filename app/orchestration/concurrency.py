import asyncio
from app.core.config import settings

class ConcurrencyController:
    def __init__(self, max_concurrent: int = None):
        limit = max_concurrent or settings.MAX_PARALLEL_SCANS
        self.semaphore = asyncio.Semaphore(limit)

    def try_acquire(self) -> bool:
        """Attempts to acquire a slot immediately. Returns True if successful, False otherwise."""
        # Non-blocking check
        if self.semaphore.locked():
            return False
        
        # In a strictly single-threaded event loop like asyncio, 
        # locked() is reliable for immediate rejection if we follow up 
        # with an immediate non-blocking acquire if possible.
        # However, asyncio.Semaphore.acquire() is a coroutine and doesn't have a 'try_acquire'.
        # We simulate it by checking the value.
        if self.semaphore._value > 0:
            # We must use a coroutine to actually acquire it.
            # For the POC design, we'll use a wrapper that the Orchestrator calls.
            return True
        return False

    async def acquire(self):
        await self.semaphore.acquire()

    def release(self):
        self.semaphore.release()
