"""
Prompts API endpoints.
"""

from fastapi import APIRouter, HTTPException, Depends, status
from typing import List

from ..store.firestore.prompts import PromptStore
from ..common.auth import validate_tenant_access, get_current_tenant
from ..models.schemas import PromptResponse, PromptStats, PromptsQueryRequest

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
        filters["decision"] = decision
    if date_from:
        filters["start_date"] = date_from
    if date_to:
        filters["end_date"] = date_to
    if user_id:
        filters["user_id"] = user_id
    if has_risks is not None:
        filters["has_risks"] = has_risks
    
    prompts = prompt_store.query_by_tenant(current_tenant, filters)
    
    # Filter by risk type if specified
    if risk_type:
        filtered_prompts = []
        for prompt in prompts:
            if prompt.get("risks"):
                for risk in prompt["risks"]:
                    risk_type_str = risk.get("type", "").upper()
                    if risk_type.upper() in risk_type_str:
                        filtered_prompts.append(prompt)
                        break
        prompts = filtered_prompts
    
    return [PromptResponse(**prompt) for prompt in prompts[:limit]]

@router.get("/prompts/{prompt_id}", response_model=PromptResponse)
async def get_prompt(
    prompt_id: str,
    current_tenant: str = Depends(get_current_tenant)
):
    """Get a specific prompt."""
    prompt = prompt_store.get_by_tenant(current_tenant, prompt_id)
    if not prompt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Prompt not found"
        )
    
    return PromptResponse(**prompt)

@router.get("/prompts/stats", response_model=PromptStats)
async def get_prompt_stats(current_tenant: str = Depends(get_current_tenant)):
    """Get prompt statistics for the current tenant."""
    stats = prompt_store.get_prompt_stats(current_tenant)
    return PromptStats(**stats)

