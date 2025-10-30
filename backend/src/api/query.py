"""
Query/prompt processing API endpoints.
"""

from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.responses import JSONResponse
import os
import asyncio
from typing import Optional

from ..store.firestore.prompts import PromptStore
from ..store.firestore.rules import RuleStore
from ..store.firestore.logs import LogStore
from ..firewall.detector import FirewallDetector
from ..firewall.rules import FirewallRules
from ..firewall.pipeline import run_detection_and_persist
from ..common.auth import get_current_tenant
from ..common.rate_limiter import check_rate_limit
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
        # Validate input size (already enforced by schema, but double-check for large inputs)
        if len(request.prompt) > 100000:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail="Prompt size exceeds maximum allowed length (100,000 characters)"
            )
        
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
        
        # Run detection+persistence in a background thread with timeout protection
        try:
            result_payload = await asyncio.wait_for(
                asyncio.to_thread(
                    run_detection_and_persist,
                    detector,
                    rules_engine,
                    prompt_store,
                    log_store,
                    tenant_id=request.tenant_id,
                    prompt=request.prompt,
                    rules=rules,
                    user_id=request.user_id or "",
                    metadata=request.metadata or {}
                ),
                timeout=10
            )
        except asyncio.TimeoutError:
            # Keep background thread running; inform client to check dashboard later
            return JSONResponse(
                status_code=status.HTTP_202_ACCEPTED,
                content={
                    "status": "processing",
                    "message": ApiConstants.BACKGROUND_PROCESSING_MESSAGE,
                },
            )
        
        return QueryResponse(
            decision=result_payload["decision"],
            promptModified=result_payload["promptModified"],
            risks=result_payload["risks"],
            prompt_id=result_payload["prompt_id"],
            timestamp=result_payload["timestamp"],
            anomaly_score=result_payload["anomaly_score"],
            confidence=result_payload["confidence"],
            reason=result_payload["reason"],
            applied_rules=result_payload["applied_rules"],
            severity=result_payload.get("severity", FirewallConstants.SEVERITY_LOW),
            risk_categories=result_payload.get("risk_categories", []),
            prompt=result_payload.get("prompt", request.prompt),
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=ApiConstants.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ApiConstants.FAILED_TO_PROCESS_PROMPT.format(str(e))
        )

