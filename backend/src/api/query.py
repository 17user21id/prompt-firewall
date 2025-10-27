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
from ..common.api_constants import ApiConstants
from ..common.auth_constants import AuthConstants
from ..common.database_constants import DatabaseConstants
from ..common.config_constants import ConfigConstants
from ..common.monitoring import MonitoringMiddleware
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
                detail=AuthConstants.ACCESS_DENIED_INVALID_TENANT
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
            DatabaseConstants.PROMPT_FIELD: request.prompt,
            DatabaseConstants.RESPONSE_FIELD: "",  # Mock response
            DatabaseConstants.DECISION_FIELD: rule_result["action"],
            DatabaseConstants.PROMPT_MODIFIED_FIELD: rule_result["modified"],
            DatabaseConstants.RISKS_FIELD: detection_result["risks"],
            DatabaseConstants.ANOMALY_SCORE_FIELD: detection_result["anomaly_score"],
            DatabaseConstants.USER_ID_FIELD: request.user_id or "",
            DatabaseConstants.METADATA_FIELD: request.metadata or {}
        }
        
        prompt_id = prompt_store.save(request.tenant_id, prompt_data)
        
        # Log detection events to monitoring if enabled
        if os.getenv(ConfigConstants.ENABLE_METRICS_COLLECTION_ENV, "false").lower() == "true":
            # Track PII detections
            for risk in detection_result["risks"]:
                if risk.get("type") == "pii":
                    MonitoringMiddleware.log_pii_detection(
                        pii_type=risk.get("category", "unknown"),
                        severity=detection_result.get("severity", FirewallConstants.SEVERITY_LOW)
                    )
                elif risk.get("type") == "injection":
                    MonitoringMiddleware.log_injection_detection(
                        injection_type=risk.get("category", "unknown"),
                        severity=detection_result.get("severity", FirewallConstants.SEVERITY_LOW)
                    )
        
        # Map action to event_type format
        event_type_mapping = {
            FirewallConstants.DECISION_BLOCK: FirewallConstants.EVENT_BLOCKED,
            FirewallConstants.DECISION_REDACT: FirewallConstants.EVENT_REDACTED,
            FirewallConstants.DECISION_WARN: FirewallConstants.EVENT_WARNED,
            FirewallConstants.DECISION_ALLOW: FirewallConstants.EVENT_PROCESSED
        }
        event_type = event_type_mapping.get(rule_result["action"], FirewallConstants.EVENT_PROCESSED)
        
        # Log the event
        log_data = {
            DatabaseConstants.PROMPT_ID_FIELD: prompt_id,
            DatabaseConstants.EVENT_TYPE_FIELD: event_type,
            DatabaseConstants.DETAILS_FIELD: {
                DatabaseConstants.PROMPT_FIELD: request.prompt,  # Include the actual prompt
                DatabaseConstants.REASON_FIELD: rule_result["reason"],
                DatabaseConstants.RISKS_DETECTED_FIELD: len(detection_result["risks"]),
                DatabaseConstants.RULES_APPLIED_FIELD: len(rule_result["applied_rules"])
            },
            DatabaseConstants.USER_ID_FIELD: request.user_id or "",
            DatabaseConstants.METADATA_FIELD: request.metadata or {},
            DatabaseConstants.SEVERITY_FIELD: detection_result.get("severity", FirewallConstants.SEVERITY_LOW),
            DatabaseConstants.RISK_CATEGORIES_FIELD: detection_result.get("detected_categories", [])
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
            severity=detection_result.get("severity", FirewallConstants.SEVERITY_LOW),
            risk_categories=detection_result.get("detected_categories", []),
            prompt=request.prompt
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=ApiConstants.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ApiConstants.FAILED_TO_PROCESS_PROMPT.format(str(e))
        )

