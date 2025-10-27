"""
Logs API endpoints.
"""

from fastapi import APIRouter, Depends, status
from typing import List

from ..store.firestore.logs import LogStore
from ..common.auth import validate_tenant_access, get_current_tenant
from ..models.schemas import LogResponse, LogStats, LogsQueryRequest

# Initialize stores
log_store = LogStore()

router = APIRouter()

@router.get("/logs", response_model=List[LogResponse])
async def get_logs(
    current_tenant: str = Depends(get_current_tenant),
    event_type: str = None,
    date_from: str = None,
    date_to: str = None,
    user_id: str = None,
    prompt_id: str = None,
    limit: int = 100
):
    """Get logs for the current tenant."""
    filters = {}
    if event_type:
        filters["event_type"] = event_type
    if date_from:
        filters["start_date"] = date_from
    if date_to:
        filters["end_date"] = date_to
    if user_id:
        filters["user_id"] = user_id
    if prompt_id:
        filters["prompt_id"] = prompt_id
    
    logs = log_store.query_by_tenant(current_tenant, filters)
    return [LogResponse(**log) for log in logs[:limit]]

@router.get("/logs/stats", response_model=LogStats)
async def get_log_stats(current_tenant: str = Depends(get_current_tenant)):
    """Get log statistics for the current tenant."""
    stats = log_store.get_log_stats(current_tenant)
    return LogStats(**stats)

@router.get("/logs/export")
async def export_logs(current_tenant: str = Depends(get_current_tenant)):
    """Export logs as CSV."""
    logs = log_store.query_by_tenant(current_tenant)
    # CSV export logic here
    return {"message": "Log export feature coming soon"}

