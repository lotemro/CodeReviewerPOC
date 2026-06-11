from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum

class ScanStatus(str, Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

class ScanBase(BaseModel):
    file_hash: str
    status: ScanStatus = ScanStatus.PENDING
    results_json: Optional[str] = None
    error_message: Optional[str] = None

class ScanCreate(ScanBase):
    id: str

class ScanInDB(ScanCreate):
    created_at: datetime
    updated_at: datetime

class ScanResponse(BaseModel):
    id: str
    status: ScanStatus
    results: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
