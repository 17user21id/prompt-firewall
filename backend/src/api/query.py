"""
Query/prompt processing API endpoints.
"""

from fastapi import APIRouter, HTTPException, Depends, status
import os

from ..store.firestore.prompts import PromptStore
from ..store.firestore.rules import RuleStore
from ..store.firestore.logs import LogStore
from ..firewall.detector import FirewallDetector
from ..firewall.rules import FirewallRules
from ..common.auth import get_current_tenant, check_rate_limit
from ..common.firewall_constants import FirewallConstants
from ..models.schemas import QueryRequest, QueryResponse

# Initialize stores and services
prompt_store = PromptStore()
rule_store = RuleStore()
log_store = LogStore()
detector = FirewallDetector(
    openai_api_key=os.getenv(FirewallConstants.OPENAI_API_KEY_ENV),
    openai_model=os.getenv(FirewallConstants.OPENAI_MODEL_ENV, FirewallConstants.DEFAULT_OPENAI_MODEL)
)
rules_engine = FirewallRules()

router = APIRouter()

@router.post("/query", response_model=QueryResponse)
async def process_prompt(
    request: QueryRequest,
    current_tenant: str = Depends(get_current_tenant)
):
    """Process a prompt for security analysis."""
    try:
        # Validate tenant access
        if current_tenant != request.tenant_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: Invalid tenant"
            )
        
        # Check rate limit
        check_rate_limit(request.tenant_id)
        
        # Get tenant rules
        rules = rule_store.get_active_rules(request.tenant_id)
        
        # Detect risks
        detection_result = detector.detect(
            request.prompt,
            custom_rules=rules,
            use_openai=bool(os.getenv("OPENAI_API_KEY"))
        )
        
        # Apply rules
        rule_result = rules_engine.apply(
            request.prompt,
            detection_result["risks"],
            rules
        )
        
        # Save prompt record
        prompt_data = {
            "prompt": request.prompt,
            "response": "",  # Mock response
            "decision": rule_result["action"],
            "promptModified": rule_result["modified"],
            "risks": detection_result["risks"],
            "anomaly_score": detection_result["anomaly_score"],
            "user_id": request.user_id or "",
            "metadata": request.metadata or {}
        }
        
        prompt_id = prompt_store.save(request.tenant_id, prompt_data)
        
        # Map action to event_type format
        event_type_mapping = {
            "block": "blocked",
            "redact": "redacted",
            "warn": "warned",
            "allow": "processed"
        }
        event_type = event_type_mapping.get(rule_result["action"], "processed")
        
        # Log the event
        log_data = {
            "prompt_id": prompt_id,
            "event_type": event_type,
            "details": {
                "prompt": request.prompt,  # Include the actual prompt
                "reason": rule_result["reason"],
                "risks_detected": len(detection_result["risks"]),
                "rules_applied": len(rule_result["applied_rules"])
            },
            "user_id": request.user_id or "",
            "metadata": request.metadata or {},
            "severity": detection_result.get("severity", "low"),
            "risk_categories": detection_result.get("detected_categories", [])
        }
        
        log_store.save(request.tenant_id, log_data)
        
        return QueryResponse(
            decision=rule_result["action"],
            promptModified=rule_result["modified"],
            risks=detection_result["risks"],
            prompt_id=prompt_id,
            timestamp=rule_result["timestamp"],
            anomaly_score=detection_result["anomaly_score"],
            confidence=detection_result["confidence"],
            reason=rule_result["reason"],
            applied_rules=rule_result["applied_rules"],
            severity=detection_result.get("severity", "low"),
            risk_categories=detection_result.get("detected_categories", []),
            prompt=request.prompt
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process prompt: {str(e)}"
        )

