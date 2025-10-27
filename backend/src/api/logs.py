"""
Logs API endpoints.
"""

from fastapi import APIRouter, Depends, status
from typing import List

from ..store.firestore.logs import LogStore
from ..store.firestore.prompts import PromptStore
from ..common.auth import validate_tenant_access, get_current_tenant
from ..models.schemas import LogResponse, LogStats, LogsQueryRequest

# Initialize stores
log_store = LogStore()
prompt_store = PromptStore()

router = APIRouter()

@router.get("/logs", response_model=List[LogResponse])
async def get_logs(
    current_tenant: str = Depends(get_current_tenant),
    event_type: str = None,
    date_from: str = None,
    date_to: str = None,
    user_id: str = None,
    prompt_id: str = None,
    limit: int = 100,
    offset: int = 0,
    risk_category: str = None,
    severity: str = None
):
    """Get logs for the current tenant with pagination and filtering."""
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
    if severity:
        filters["severity"] = severity
    
    logs = log_store.query_by_tenant(current_tenant, filters)
    
    # Convert old event_type values to new format
    event_type_conversion = {
        "block": "blocked",
        "redact": "redacted",
        "warn": "warned",
        "allow": "processed"
    }
    
    converted_logs = []
    for log in logs:
        if "event_type" in log:
            log["event_type"] = event_type_conversion.get(log["event_type"], log["event_type"])
        
        # If prompt is not in log details, fetch it from prompts table using prompt_id
        if "details" in log and "prompt" not in log.get("details", {}):
            prompt_id = log.get("prompt_id", "")
            if prompt_id:
                try:
                    prompt_data = prompt_store.get_by_tenant(current_tenant, prompt_id)
                    if prompt_data and "prompt" in prompt_data:
                        log["details"]["prompt"] = prompt_data["prompt"]
                except Exception as e:
                    # If prompt fetch fails, leave it as is
                    pass
        
        # Filter by risk category if provided
        if risk_category:
            # Check if risk_category matches any risk in the log
            log_risks = log.get("details", {}).get("risks", [])
            if log_risks:
                category_match = any(
                    risk.get("category", "").upper() == risk_category.upper() or
                    risk.get("type", "").upper().startswith(risk_category.upper())
                    for risk in log_risks if isinstance(risk, dict)
                )
                if not category_match:
                    continue
        
        converted_logs.append(log)
    
    # Apply pagination
    paginated_logs = converted_logs[offset:offset + limit]
    
    return [LogResponse(**log) for log in paginated_logs]

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

