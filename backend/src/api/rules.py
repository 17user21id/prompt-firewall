"""
Rules management API endpoints.
"""

from fastapi import APIRouter, HTTPException, Depends, status
from typing import List

from ..store.firestore.rules import RuleStore
from ..firewall.rules import FirewallRules
from ..firewall.detection_patterns import DetectionPatternRegistry
from ..common.auth import validate_tenant_access, log_auth_event, get_current_tenant
from ..models.schemas import RuleCreate, RuleUpdate, RuleResponse, RuleStats, RulesQueryRequest

# Initialize stores
rule_store = RuleStore()
rules_engine = FirewallRules()

router = APIRouter()

@router.get("/rules", response_model=List[RuleResponse])
async def get_rules(
    current_tenant: str = Depends(get_current_tenant),
    rule_type: str = None,
    action: str = None,
    severity: str = None,
    enabled: bool = None,
    limit: int = 100
):
    """Get rules for the current tenant."""
    filters = {}
    if rule_type:
        filters["type"] = rule_type
    if action:
        filters["action"] = action
    if severity:
        filters["severity"] = severity
    if enabled is not None:
        filters["enabled"] = enabled
    
    rules = rule_store.query_by_tenant(current_tenant, filters)
    return [RuleResponse(**rule) for rule in rules[:limit]]

@router.post("/rules", response_model=RuleResponse)
async def create_rule(
    request: RuleCreate,
    current_tenant: str = Depends(get_current_tenant)
):
    """Create a new rule for the current tenant."""
    try:
        # Validate rule
        validation_result = rules_engine.validate_rule(request.dict())
        if not validation_result["valid"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid rule: {', '.join(validation_result['errors'])}"
            )
        
        rule_id = rule_store.save(current_tenant, request.dict())
        rule = rule_store.get_by_tenant(current_tenant, rule_id)
        
        # Log rule creation
        log_auth_event(current_tenant, "rule_created", {
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
    current_tenant: str = Depends(get_current_tenant)
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
        
        success = rule_store.update_by_tenant(current_tenant, rule_id, request.dict())
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Rule not found"
            )
        
        rule = rule_store.get_by_tenant(current_tenant, rule_id)
        
        # Log rule update
        log_auth_event(current_tenant, "rule_updated", {
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
    current_tenant: str = Depends(get_current_tenant)
):
    """Delete a rule."""
    try:
        success = rule_store.delete_by_tenant(current_tenant, rule_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Rule not found"
            )
        
        # Log rule deletion
        log_auth_event(current_tenant, "rule_deleted", {
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
async def get_rule_stats(current_tenant: str = Depends(get_current_tenant)):
    """Get rule statistics for the current tenant."""
    stats = rule_store.get_rule_stats(current_tenant)
    return RuleStats(**stats)

@router.get("/patterns")
async def get_all_patterns(current_tenant: str = Depends(get_current_tenant)):
    """Get all active detection patterns (built-in + custom rules)."""
    try:
        # Get custom rules from Firestore
        custom_rules = rule_store.query_by_tenant(current_tenant, {"enabled": True})
        
        # Get built-in patterns from DetectionPatternRegistry
        built_in_patterns = DetectionPatternRegistry.get_all_patterns()
        
        # Format built-in patterns
        built_in_list = []
        for pattern in built_in_patterns:
            built_in_list.append({
                "pattern_id": f"builtin_{pattern.name}",
                "type": pattern.category.value,
                "pattern": pattern.pattern.pattern,  # Get regex pattern string
                "action": pattern.action,
                "severity": pattern.severity,
                "confidence": pattern.confidence,
                "description": pattern.description,
                "source": "built-in",
                "enabled": True
            })
        
        # Format custom rules
        custom_list = []
        for rule in custom_rules:
            custom_list.append({
                "pattern_id": rule.get("rule_id", ""),
                "type": rule.get("type", ""),
                "pattern": rule.get("pattern", ""),
                "action": rule.get("action", ""),
                "severity": rule.get("severity", ""),
                "description": rule.get("description", ""),
                "source": "custom",
                "enabled": rule.get("enabled", True),
                "created_at": rule.get("created_at", ""),
                "updated_at": rule.get("updated_at", "")
            })
        
        return {
            "built_in_patterns": built_in_list,
            "custom_rules": custom_list,
            "total_built_in": len(built_in_list),
            "total_custom": len(custom_list),
            "total_active": len(built_in_list) + len(custom_list)
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get patterns: {str(e)}"
        )

