"""
Logs API endpoints.
"""

from fastapi import APIRouter, Depends
from typing import List

from ..store.firestore.logs import LogStore
from ..store.firestore.prompts import PromptStore
from ..common.auth import get_current_tenant
from ..common.api_constants import ApiConstants
from ..common.firewall_constants import FirewallConstants
from ..common.database_constants import DatabaseConstants
from ..models.schemas import LogResponse

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
        filters[DatabaseConstants.EVENT_TYPE_FIELD] = event_type
    if date_from:
        filters[DatabaseConstants.START_DATE_FIELD] = date_from
    if date_to:
        filters[DatabaseConstants.END_DATE_FIELD] = date_to
    if user_id:
        filters[DatabaseConstants.USER_ID_FIELD] = user_id
    if prompt_id:
        filters[DatabaseConstants.PROMPT_ID_FIELD] = prompt_id
    if severity:
        filters[DatabaseConstants.SEVERITY_FIELD] = severity
    
    logs = log_store.query_by_tenant(current_tenant, filters)
    
    # Convert old event_type values to new format
    event_type_conversion = {
        FirewallConstants.DECISION_BLOCK: FirewallConstants.EVENT_BLOCKED,
        FirewallConstants.DECISION_REDACT: FirewallConstants.EVENT_REDACTED,
        FirewallConstants.DECISION_WARN: FirewallConstants.EVENT_WARNED,
        FirewallConstants.DECISION_ALLOW: FirewallConstants.EVENT_PROCESSED
    }
    
    # OPTIMIZATION: Batch fetch prompts instead of N+1 queries
    # Collect all prompt IDs that need to be fetched
    prompt_ids_to_fetch = []
    logs_needing_prompts = []
    
    for log in logs:
        # Convert old event_type values to new format
        if DatabaseConstants.EVENT_TYPE_FIELD in log:
            log[DatabaseConstants.EVENT_TYPE_FIELD] = event_type_conversion.get(log[DatabaseConstants.EVENT_TYPE_FIELD], log[DatabaseConstants.EVENT_TYPE_FIELD])
        
        # Collect logs that need prompt data
        if DatabaseConstants.DETAILS_FIELD in log and DatabaseConstants.PROMPT_FIELD not in log.get(DatabaseConstants.DETAILS_FIELD, {}):
            prompt_id = log.get(DatabaseConstants.PROMPT_ID_FIELD, "")
            if prompt_id:
                prompt_ids_to_fetch.append(prompt_id)
                logs_needing_prompts.append((log, prompt_id))
    
    # Batch fetch all prompts at once
    prompts_dict = {}
    if prompt_ids_to_fetch:
        try:
            # Use batch fetch method to avoid N+1 queries
            prompts_dict = prompt_store.get_batch(current_tenant, list(set(prompt_ids_to_fetch)))
        except Exception as e:
            # If batch fetch fails, fallback to empty dict
            pass
    
    # Attach prompt data to logs
    for log, prompt_id in logs_needing_prompts:
        if prompt_id in prompts_dict:
            prompt_data = prompts_dict[prompt_id]
            if prompt_data and DatabaseConstants.PROMPT_FIELD in prompt_data:
                log[DatabaseConstants.DETAILS_FIELD][DatabaseConstants.PROMPT_FIELD] = prompt_data[DatabaseConstants.PROMPT_FIELD]
    
    # Filter by risk category if provided
    converted_logs = []
    for log in logs:
        if risk_category:
            # Check if risk_category matches any risk in the log
            log_risks = log.get(DatabaseConstants.DETAILS_FIELD, {}).get(DatabaseConstants.RISKS_FIELD, [])
            if log_risks:
                category_match = any(
                    risk.get(DatabaseConstants.CATEGORY_FIELD, "").upper() == risk_category.upper() or
                    risk.get(DatabaseConstants.TYPE_FIELD, "").upper().startswith(risk_category.upper())
                    for risk in log_risks if isinstance(risk, dict)
                )
                if not category_match:
                    continue
        
        converted_logs.append(log)
    
    # Apply pagination
    paginated_logs = converted_logs[offset:offset + limit]
    
    return [LogResponse(**log) for log in paginated_logs]

@router.get("/logs/export")
async def export_logs(current_tenant: str = Depends(get_current_tenant)):
    """Export logs as CSV."""
    logs = log_store.query_by_tenant(current_tenant)
    # CSV export logic here
    return {DatabaseConstants.MESSAGE_FIELD: ApiConstants.LOG_EXPORT_COMING_SOON}

