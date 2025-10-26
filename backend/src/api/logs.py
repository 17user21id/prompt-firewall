"""
Logs API endpoints.
"""

from fastapi import APIRouter, Depends, status
from typing import List

from ..store.firestore.logs import LogStore
from ..common.auth import validate_tenant_access
from ..models.schemas import LogResponse, LogStats, LogsQueryRequest

# Initialize stores
log_store = LogStore()

router = APIRouter()

@router.get("/logs", response_model=List[LogResponse])
async def get_logs(
    tenant_id: str = Depends(validate_tenant_access),
    request: LogsQueryRequest = Depends()
):
    """Get logs for a tenant."""
    filters = {}
    if request.event_type:
        filters["event_type"] = request.event_type
    if request.start_date:
        filters["start_date"] = request.start_date
    if request.end_date:
        filters["end_date"] = request.end_date
    
    logs = log_store.query_by_tenant(tenant_id, filters)
    return [LogResponse(**log) for log in logs]

@router.get("/logs/stats", response_model=LogStats)
async def get_log_stats(tenant_id: str = Depends(validate_tenant_access)):
    """Get log statistics for a tenant."""
    stats = log_store.get_log_stats(tenant_id)
    return LogStats(**stats)

@router.get("/logs/export")
async def export_logs(tenant_id: str = Depends(validate_tenant_access)):
    """Export logs as CSV."""
    logs = log_store.query_by_tenant(tenant_id)
    # CSV export logic here
    return {"message": "Log export feature coming soon"}

