"""
Prompts API endpoints.
"""

from fastapi import APIRouter, Depends
from typing import List

from ..store.firestore.prompts import PromptStore
from ..common.auth import get_current_tenant
from ..common.database_constants import DatabaseConstants
from ..models.schemas import PromptResponse

# Initialize stores
prompt_store = PromptStore()

router = APIRouter()

@router.get("/prompts", response_model=List[PromptResponse])
async def get_prompts(
    current_tenant: str = Depends(get_current_tenant),
    decision: str = None,
    date_from: str = None,
    date_to: str = None,
    user_id: str = None,
    has_risks: bool = None,
    risk_type: str = None,
    limit: int = 100
):
    """Get prompts for the current tenant with filtering."""
    filters = {}
    if decision:
        filters[DatabaseConstants.DECISION_FIELD] = decision
    if date_from:
        filters[DatabaseConstants.START_DATE_FIELD] = date_from
    if date_to:
        filters[DatabaseConstants.END_DATE_FIELD] = date_to
    if user_id:
        filters[DatabaseConstants.USER_ID_FIELD] = user_id
    if has_risks is not None:
        filters[DatabaseConstants.HAS_RISKS_FIELD] = has_risks
    
    prompts = prompt_store.query_by_tenant(current_tenant, filters)
    
    # Filter by risk type if specified
    if risk_type:
        filtered_prompts = []
        for prompt in prompts:
            if prompt.get(DatabaseConstants.RISKS_FIELD):
                for risk in prompt[DatabaseConstants.RISKS_FIELD]:
                    risk_type_str = risk.get(DatabaseConstants.TYPE_FIELD, "").upper()
                    if risk_type.upper() in risk_type_str:
                        filtered_prompts.append(prompt)
                        break
        prompts = filtered_prompts
    
    return [PromptResponse(**prompt) for prompt in prompts[:limit]]

