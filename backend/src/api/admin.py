"""
Admin API endpoints.
"""

from fastapi import APIRouter, Depends
from typing import List
from datetime import datetime

from ..store.firestore.tenants import TenantStore
from ..store.firestore.prompts import PromptStore
from ..store.firestore.rules import RuleStore
from ..store.firestore.logs import LogStore
from ..common.auth import validate_tenant_access, require_admin_access
from ..models.schemas import (
    TenantResponse, TenantStats,
    PromptStats, RuleStats, LogStats, StatsResponse
)

# Initialize stores
tenant_store = TenantStore()
prompt_store = PromptStore()
rule_store = RuleStore()
log_store = LogStore()

router = APIRouter()

@router.get("/admin/tenants", response_model=List[TenantResponse])
async def list_all_tenants(admin_tenant: str = Depends(require_admin_access)):
    """List all tenants (admin only)."""
    tenants = tenant_store.get_all_tenants()
    return [TenantResponse(**tenant) for tenant in tenants]

@router.get("/stats", response_model=StatsResponse)
async def get_all_stats(tenant_id: str = Depends(validate_tenant_access)):
    """Get comprehensive statistics for a tenant."""
    tenant_stats = tenant_store.get_tenant_stats(tenant_id)
    prompt_stats = prompt_store.get_prompt_stats(tenant_id)
    rule_stats = rule_store.get_rule_stats(tenant_id)
    log_stats = log_store.get_log_stats(tenant_id)
    
    return StatsResponse(
        tenant_stats=TenantStats(**tenant_stats) if tenant_stats else None,
        prompt_stats=PromptStats(**prompt_stats) if prompt_stats else None,
        rule_stats=RuleStats(**rule_stats) if rule_stats else None,
        log_stats=LogStats(**log_stats) if log_stats else None,
        timestamp=datetime.utcnow().isoformat()
    )

