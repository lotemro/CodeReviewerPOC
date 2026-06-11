import aiosqlite
import json
from typing import Optional, List
from datetime import datetime, timedelta, timezone
from app.db.models import ScanInDB, ScanStatus, ScanCreate

class ScanRepository:
    def __init__(self, db: aiosqlite.Connection):
        self.db = db

    async def create_scan(self, scan: ScanCreate) -> ScanInDB:
        await self.db.execute(
            """
            INSERT INTO scans (id, file_hash, status, results_json, error_message)
            VALUES (?, ?, ?, ?, ?)
            """,
            (scan.id, scan.file_hash, scan.status.value, scan.results_json, scan.error_message)
        )
        await self.db.commit()
        return await self.get_scan_by_id(scan.id)

    async def get_scan_by_id(self, scan_id: str) -> Optional[ScanInDB]:
        async with self.db.execute("SELECT * FROM scans WHERE id = ?", (scan_id,)) as cursor:
            row = await cursor.fetchone()
            if row:
                return ScanInDB(**dict(row))
            return None

    async def get_completed_scan_by_hash(self, file_hash: str) -> Optional[ScanInDB]:
        async with self.db.execute(
            "SELECT * FROM scans WHERE file_hash = ? AND status = ? ORDER BY created_at DESC LIMIT 1",
            (file_hash, ScanStatus.COMPLETED.value)
        ) as cursor:
            row = await cursor.fetchone()
            if row:
                return ScanInDB(**dict(row))
            return None

    async def update_scan_status(self, scan_id: str, status: ScanStatus, results_json: Optional[str] = None, error_message: Optional[str] = None):
        await self.db.execute(
            """
            UPDATE scans 
            SET status = ?, results_json = ?, error_message = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (status.value, results_json, error_message, scan_id)
        )
        await self.db.commit()

    async def mark_pending_and_running_as_failed(self):
        await self.db.execute(
            "UPDATE scans SET status = ?, error_message = ? WHERE status IN (?, ?)",
            (ScanStatus.FAILED.value, "Scan interrupted by system restart", ScanStatus.PENDING.value, ScanStatus.RUNNING.value)
        )
        await self.db.commit()

    async def delete_old_scans(self, hours: int):
        # SQLite CURRENT_TIMESTAMP is UTC
        cutoff = (datetime.now(timezone.utc) - timedelta(hours=hours)).strftime('%Y-%m-%d %H:%M:%S')
        await self.db.execute("DELETE FROM scans WHERE created_at < ?", (cutoff,))
        await self.db.commit()
