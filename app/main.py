import asyncio
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.api.routes import router
from app.db.database import init_db, get_db
from app.db.repository import ScanRepository
from app.orchestration.lifecycle import run_recovery, cleanup_loop
from app.core.config import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic
    await init_db()
    
    # Initialize repository for lifecycle tasks
    # We use a direct connection here as we are outside the request context
    from aiosqlite import connect
    async with connect(settings.DB_PATH) as db:
        repo = ScanRepository(db)
        await run_recovery(repo)
    
    # Start cleanup loop in background
    cleanup_task = asyncio.create_task(cleanup_loop(ScanRepository(await connect(settings.DB_PATH))))
    
    yield
    
    # Shutdown logic
    cleanup_task.cancel()
    try:
        await cleanup_task
    except asyncio.CancelledError:
        logger.info("Cleanup task cancelled successfully.")

app = FastAPI(
    title=settings.PROJECT_NAME,
    lifespan=lifespan
)

app.include_router(router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
