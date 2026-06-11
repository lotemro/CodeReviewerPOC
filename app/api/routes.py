from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from app.db.models import ScanResponse, ScanStatus
from app.orchestration.orchestrator import ScanOrchestrator, CapacityReachedException
from app.db.database import get_db
from app.db.repository import ScanRepository
from app.reviewer.engine import ReviewerEngine
from app.llm.factory import get_llm_client
from app.orchestration.concurrency import ConcurrencyController
import aiosqlite

router = APIRouter()

# Global instances (in a larger app, these would be managed by a DI container or lifespan)
concurrency_controller = ConcurrencyController()
llm_client = get_llm_client()
engine = ReviewerEngine(llm_client)

# Dependencies
def get_concurrency_controller() -> ConcurrencyController:
    # In a real app, this might be stored in app.state
    # For now, we keep it as a singleton at the module level but access via dependency
    return concurrency_controller

def get_engine() -> ReviewerEngine:
    return engine

async def get_orchestrator(
    db: aiosqlite.Connection = Depends(get_db),
    engine: ReviewerEngine = Depends(get_engine),
    cc: ConcurrencyController = Depends(get_concurrency_controller)
) -> ScanOrchestrator:
    repository = ScanRepository(db)
    return ScanOrchestrator(repository, engine, cc)

@router.post("/scans", response_model=ScanResponse, status_code=202)
async def request_scan(
    file: UploadFile = File(...),
    orchestrator: ScanOrchestrator = Depends(get_orchestrator)
):
    if not file.filename.endswith(".py"):
        raise HTTPException(status_code=400, detail="Only .py files are supported")
    
    content = await file.read()
    code = content.decode("utf-8")
    
    try:
        response, is_new = await orchestrator.request_scan(code)
        
        # If it's a cache hit, return 200 OK instead of 202 Accepted
        if not is_new:
            # We override the status code manually because FastAPI's default for the route is 202
            # Alternatively, we could return a custom Response object
            from fastapi.responses import JSONResponse
            return JSONResponse(status_code=200, content=response.model_dump())
            
        return response
    except CapacityReachedException as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

@router.get("/scans/{scan_id}", response_model=ScanResponse)
async def get_scan(
    scan_id: str,
    orchestrator: ScanOrchestrator = Depends(get_orchestrator)
):
    result = await orchestrator.get_scan_result(scan_id)
    if not result:
        raise HTTPException(status_code=404, detail="Scan not found")
    return result
