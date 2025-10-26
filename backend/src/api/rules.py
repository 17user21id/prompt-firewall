"""
Rules management API endpoints.
"""

from fastapi import APIRouter, HTTPException, Depends, status
from typing import List

from ..store.firestore.rules import RuleStore
from ..firewall.rules import FirewallRules
from ..common.auth import validate_tenant_access, log_auth_event
from ..models.schemas import RuleCreate, RuleUpdate, RuleResponse, RuleStats, RulesQueryRequest

# Initialize stores
rule_store = RuleStore()
rules_engine = FirewallRules()

router = APIRouter()

@router.get("/rules", response_model=List[RuleResponse])
async def get_rules(
    tenant_id: str = Depends(validate_tenant_access),
    request: RulesQueryRequest = Depends()
):
    """Get rules for a tenant."""
    filters = {}
    if request.type:
        filters["type"] = request.type
    if request.action:
        filters["action"] = request.action
    if request.severity:
        filters["severity"] = request.severity
    if request.enabled is not None:
        filters["enabled"] = request.enabled
    
    rules = rule_store.query_by_tenant(tenant_id, filters)
    return [RuleResponse(**rule) for rule in rules]

@router.post("/rules", response_model=RuleResponse)
async def create_rule(
    request: RuleCreate,
    tenant_id: str = Depends(validate_tenant_access)
):
    """Create a new rule for a tenant."""
    try:
        # Validate rule
        validation_result = rules_engine.validate_rule(request.dict())
        if not validation_result["valid"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid rule: {', '.join(validation_result['errors'])}"
            )
        
        rule_id = rule_store.save(tenant_id, request.dict())
        rule = rule_store.get_by_tenant(tenant_id, rule_id)
        
        # Log rule creation
        log_auth_event(tenant_id, "rule_created", {
            "rule_id": rule_id,
            "rule_type": request.type,
            "action": request.action
        })
        
        return RuleResponse(**rule)
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create rule: {str(e)}"
        )

@router.put("/rules/{rule_id}", response_model=RuleResponse)
async def update_rule(
    rule_id: str,
    request: RuleUpdate,
    tenant_id: str = Depends(validate_tenant_access)
):
    """Update a rule."""
    try:
        # Validate rule if pattern is provided
        if request.pattern:
            validation_result = rules_engine.validate_rule(request.dict())
            if not validation_result["valid"]:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid rule: {', '.join(validation_result['errors'])}"
                )
        
        success = rule_store.update_by_tenant(tenant_id, rule_id, request.dict())
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Rule not found"
            )
        
        rule = rule_store.get_by_tenant(tenant_id, rule_id)
        
        # Log rule update
        log_auth_event(tenant_id, "rule_updated", {
            "rule_id": rule_id,
            "updated_fields": list(request.dict(exclude_unset=True).keys())
        })
        
        return RuleResponse(**rule)
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update rule: {str(e)}"
        )

@router.delete("/rules/{rule_id}")
async def delete_rule(
    rule_id: str,
    tenant_id: str = Depends(validate_tenant_access)
):
    """Delete a rule."""
    try:
        success = rule_store.delete_by_tenant(tenant_id, rule_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Rule not found"
            )
        
        # Log rule deletion
        log_auth_event(tenant_id, "rule_deleted", {
            "rule_id": rule_id
        })
        
        return {"message": "Rule deleted successfully"}
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete rule: {str(e)}"
        )

@router.get("/rules/stats", response_model=RuleStats)
async def get_rule_stats(tenant_id: str = Depends(validate_tenant_access)):
    """Get rule statistics for a tenant."""
    stats = rule_store.get_rule_stats(tenant_id)
    return RuleStats(**stats)

