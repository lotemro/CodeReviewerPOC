import asyncio
from app.core.config import settings

class ConcurrencyController:
    def __init__(self, max_concurrent: int = None):
        limit = max_concurrent or settings.MAX_PARALLEL_SCANS
        self.semaphore = asyncio.Semaphore(limit)
        self._background_tasks = set()

    def register_task(self, task: asyncio.Task):
        """
        Adds a task to the background tasks registry to prevent garbage collection.
        Automatically removes it when the task is done.
        """
        self._background_tasks.add(task)
        task.add_done_callback(self._background_tasks.discard)

    def try_acquire(self) -> bool:
        """
        Attempts to acquire a slot immediately without awaiting.
        Returns True if a slot was successfully acquired, False otherwise.
        """
        if not self.semaphore.locked():
            # In asyncio.Semaphore, acquire() is a coroutine. 
            # To acquire non-blockingly, we can use the same logic as the internal 
            # implementation but without the 'await' on a Future.
            if self.semaphore._value > 0:
                self.semaphore._value -= 1
                return True
        return False

    def release(self):
        """Releases a slot back to the semaphore."""
        self.semaphore.release()
