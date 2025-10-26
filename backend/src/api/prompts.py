"""
Prompts API endpoints.
"""

from fastapi import APIRouter, HTTPException, Depends, status
from typing import List

from ..store.firestore.prompts import PromptStore
from ..common.auth import validate_tenant_access
from ..models.schemas import PromptResponse, PromptStats, PromptsQueryRequest

# Initialize stores
prompt_store = PromptStore()

router = APIRouter()

@router.get("/prompts", response_model=List[PromptResponse])
async def get_prompts(
    tenant_id: str = Depends(validate_tenant_access),
    request: PromptsQueryRequest = Depends()
):
    """Get prompts for a tenant."""
    filters = {}
    if request.decision:
        filters["decision"] = request.decision
    if request.start_date:
        filters["start_date"] = request.start_date
    if request.end_date:
        filters["end_date"] = request.end_date
    
    prompts = prompt_store.query_by_tenant(tenant_id, filters)
    return [PromptResponse(**prompt) for prompt in prompts]

@router.get("/prompts/{prompt_id}", response_model=PromptResponse)
async def get_prompt(
    prompt_id: str,
    tenant_id: str = Depends(validate_tenant_access)
):
    """Get a specific prompt."""
    prompt = prompt_store.get_by_tenant(tenant_id, prompt_id)
    if not prompt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Prompt not found"
        )
    
    return PromptResponse(**prompt)

@router.get("/prompts/stats", response_model=PromptStats)
async def get_prompt_stats(tenant_id: str = Depends(validate_tenant_access)):
    """Get prompt statistics for a tenant."""
    stats = prompt_store.get_prompt_stats(tenant_id)
    return PromptStats(**stats)

