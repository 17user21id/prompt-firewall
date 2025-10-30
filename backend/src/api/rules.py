"""
Rules management API endpoints.
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict

from ..store.firestore.rules import RuleStore
from ..firewall.rules import FirewallRules
from ..firewall.detection_patterns import DetectionPatternRegistry
from ..common.auth import log_auth_event, get_current_tenant
from ..common.api_constants import ApiConstants
from ..common.firewall_constants import FirewallConstants
from ..common.database_constants import DatabaseConstants
from ..models.schemas import RuleCreate, RuleUpdate, RuleResponse

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
        filters[DatabaseConstants.TYPE_FIELD] = rule_type
    if action:
        filters[DatabaseConstants.ACTION_FIELD] = action
    if severity:
        filters[DatabaseConstants.SEVERITY_FIELD] = severity
    if enabled is not None:
        filters[DatabaseConstants.ENABLED_FIELD] = enabled
    
    rules = rule_store.query_by_tenant(current_tenant, filters)
    return [RuleResponse(**rule) for rule in rules[:limit]]

@router.get("/rules/grouped", response_model=Dict[str, List[RuleResponse]])
async def get_rules_grouped(
    current_tenant: str = Depends(get_current_tenant),
    rule_type: str = None,
    action: str = None,
    severity: str = None,
    enabled: bool = None,
    include_disabled: bool = False,
    limit: int = 100
):
    """Get rules for the current tenant grouped by type.

    Defaults to only active rules unless include_disabled is True or enabled filter is explicitly provided.
    """
    filters = {}
    if rule_type:
        filters[DatabaseConstants.TYPE_FIELD] = rule_type
    if action:
        filters[DatabaseConstants.ACTION_FIELD] = action
    if severity:
        filters[DatabaseConstants.SEVERITY_FIELD] = severity
    # If enabled filter not passed, default to active unless include_disabled=True
    if enabled is not None:
        filters[DatabaseConstants.ENABLED_FIELD] = enabled
    elif not include_disabled:
        filters[DatabaseConstants.ENABLED_FIELD] = True

    rules = rule_store.query_by_tenant(current_tenant, filters)

    grouped: Dict[str, List[RuleResponse]] = {}
    for rule in rules[:limit]:
        try:
            resp = RuleResponse(**rule)
        except Exception:
            # Skip invalid records silently from grouped view
            continue
        grouped.setdefault(resp.type, []).append(resp)

    return grouped

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
                status_code=ApiConstants.HTTP_400_BAD_REQUEST,
                detail=ApiConstants.INVALID_RULE.format(', '.join(validation_result['errors']))
            )
        
        rule_id = rule_store.save(current_tenant, request.dict())
        rule = rule_store.get_by_tenant(current_tenant, rule_id)
        
        # Log rule creation
        log_auth_event(current_tenant, FirewallConstants.EVENT_RULE_CREATED, {
            DatabaseConstants.RULE_ID_FIELD: rule_id,
            DatabaseConstants.RULE_TYPE_FIELD: request.type,
            DatabaseConstants.ACTION_FIELD: request.action
        })
        
        return RuleResponse(**rule)
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=ApiConstants.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ApiConstants.FAILED_TO_CREATE_RULE.format(str(e))
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
                    status_code=ApiConstants.HTTP_400_BAD_REQUEST,
                    detail=ApiConstants.INVALID_RULE.format(', '.join(validation_result['errors']))
                )
        
        success = rule_store.update_by_tenant(current_tenant, rule_id, request.dict())
        if not success:
            raise HTTPException(
                status_code=ApiConstants.HTTP_404_NOT_FOUND,
                detail=ApiConstants.RULE_NOT_FOUND
            )
        
        rule = rule_store.get_by_tenant(current_tenant, rule_id)
        
        # Log rule update
        log_auth_event(current_tenant, FirewallConstants.EVENT_RULE_UPDATED, {
            DatabaseConstants.RULE_ID_FIELD: rule_id,
            DatabaseConstants.UPDATED_FIELDS_FIELD: list(request.dict(exclude_unset=True).keys())
        })
        
        return RuleResponse(**rule)
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=ApiConstants.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ApiConstants.FAILED_TO_UPDATE_RULE.format(str(e))
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
                status_code=ApiConstants.HTTP_404_NOT_FOUND,
                detail=ApiConstants.RULE_NOT_FOUND
            )
        
        # Log rule deletion
        log_auth_event(current_tenant, FirewallConstants.EVENT_RULE_DELETED, {
            DatabaseConstants.RULE_ID_FIELD: rule_id
        })
        
        return {DatabaseConstants.MESSAGE_FIELD: ApiConstants.RULE_DELETED_SUCCESSFULLY}
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=ApiConstants.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ApiConstants.FAILED_TO_DELETE_RULE.format(str(e))
        )

@router.get("/patterns")
async def get_all_patterns(current_tenant: str = Depends(get_current_tenant)):
    """Get all active detection patterns (built-in + custom rules)."""
    try:
        # Get custom rules from Firestore
        custom_rules = rule_store.query_by_tenant(current_tenant, {DatabaseConstants.ENABLED_FIELD: True})
        
        # Get built-in patterns from DetectionPatternRegistry
        built_in_patterns = DetectionPatternRegistry.get_all_patterns()
        
        # Format built-in patterns
        built_in_list = []
        for pattern in built_in_patterns:
            built_in_list.append({
                DatabaseConstants.PATTERN_ID_FIELD: f"builtin_{pattern.name}",
                DatabaseConstants.TYPE_FIELD: pattern.category.value,
                DatabaseConstants.PATTERN_VALUE_FIELD: pattern.pattern.pattern,  # Get regex pattern string
                DatabaseConstants.ACTION_FIELD: pattern.action,
                DatabaseConstants.SEVERITY_FIELD: pattern.severity,
                DatabaseConstants.CONFIDENCE_FIELD: pattern.confidence,
                DatabaseConstants.DESCRIPTION_FIELD: pattern.description,
                DatabaseConstants.SOURCE_FIELD: DatabaseConstants.BUILT_IN_SOURCE,
                DatabaseConstants.ENABLED_FIELD: True
            })
        
        # Format custom rules
        custom_list = []
        for rule in custom_rules:
            custom_list.append({
                DatabaseConstants.PATTERN_ID_FIELD: rule.get("rule_id", ""),
                DatabaseConstants.TYPE_FIELD: rule.get("type", ""),
                DatabaseConstants.PATTERN_VALUE_FIELD: rule.get("pattern", ""),
                DatabaseConstants.ACTION_FIELD: rule.get("action", ""),
                DatabaseConstants.SEVERITY_FIELD: rule.get("severity", ""),
                DatabaseConstants.DESCRIPTION_FIELD: rule.get("description", ""),
                DatabaseConstants.SOURCE_FIELD: DatabaseConstants.CUSTOM_SOURCE,
                DatabaseConstants.ENABLED_FIELD: rule.get(DatabaseConstants.ENABLED_FIELD, True),
                DatabaseConstants.CREATED_AT_FIELD: rule.get(DatabaseConstants.CREATED_AT_FIELD, ""),
                DatabaseConstants.UPDATED_AT_FIELD: rule.get(DatabaseConstants.UPDATED_AT_FIELD, "")
            })
        
        return {
            DatabaseConstants.BUILT_IN_PATTERNS_FIELD: built_in_list,
            DatabaseConstants.CUSTOM_RULES_FIELD: custom_list,
            DatabaseConstants.TOTAL_BUILT_IN_FIELD: len(built_in_list),
            DatabaseConstants.TOTAL_CUSTOM_FIELD: len(custom_list),
            DatabaseConstants.TOTAL_ACTIVE_FIELD: len(built_in_list) + len(custom_list)
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=ApiConstants.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ApiConstants.FAILED_TO_GET_PATTERNS.format(str(e))
        )

