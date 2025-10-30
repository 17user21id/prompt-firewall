"""
End-to-end detection pipeline that performs detection and persistence.

This module centralizes the detection + rules application + redaction +
prompt/log persistence so it can be run in a background thread.
"""

import os
from typing import Dict, Any, List

from .detector import FirewallDetector
from .rules import FirewallRules
from ..common.firewall_constants import FirewallConstants
from ..common.database_constants import DatabaseConstants
from ..common.config_constants import ConfigConstants
from ..common.monitoring import MonitoringMiddleware


def run_detection_and_persist(
    detector: FirewallDetector,
    rules_engine: FirewallRules,
    prompt_store,
    log_store,
    *,
    tenant_id: str,
    prompt: str,
    rules: List[Dict[str, Any]],
    user_id: str = "",
    metadata: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    """
    Perform detection, apply rules, redact, persist prompt and logs, and
    return a dictionary compatible with the QueryResponse model.
    """
    if metadata is None:
        metadata = {}

    # Detect risks
    detection_result = detector.detect(
        prompt,
        custom_rules=rules,
        use_openai=bool(os.getenv("OPENAI_API_KEY"))
    )

    # Apply rules
    rule_result = rules_engine.apply(
        prompt,
        detection_result["risks"],
        rules,
    )

    # Redact PII/PHI/PCI from prompt before storing
    redacted_prompt = detector.redact_text(prompt, detection_result["risks"], redact_all_pii=True)

    # Save prompt record
    prompt_data = {
        DatabaseConstants.PROMPT_FIELD: redacted_prompt,
        DatabaseConstants.RESPONSE_FIELD: "",  # Placeholder for model response if any
        DatabaseConstants.DECISION_FIELD: rule_result["action"],
        DatabaseConstants.PROMPT_MODIFIED_FIELD: rule_result["modified"],
        DatabaseConstants.RISKS_FIELD: detection_result["risks"],
        DatabaseConstants.ANOMALY_SCORE_FIELD: detection_result["anomaly_score"],
        DatabaseConstants.USER_ID_FIELD: user_id or "",
        DatabaseConstants.METADATA_FIELD: metadata or {},
    }

    prompt_id = prompt_store.save(tenant_id, prompt_data)

    # Optional monitoring hooks
    if os.getenv(ConfigConstants.ENABLE_METRICS_COLLECTION_ENV, "false").lower() == "true":
        for risk in detection_result["risks"]:
            if risk.get("type") == "pii":
                MonitoringMiddleware.log_pii_detection(
                    pii_type=risk.get("category", "unknown"),
                    severity=detection_result.get("severity", FirewallConstants.SEVERITY_LOW),
                )
            elif risk.get("type") == "injection":
                MonitoringMiddleware.log_injection_detection(
                    injection_type=risk.get("category", "unknown"),
                    severity=detection_result.get("severity", FirewallConstants.SEVERITY_LOW),
                )

    # Map action to event type for logs
    event_type_mapping = {
        FirewallConstants.DECISION_BLOCK: FirewallConstants.EVENT_BLOCKED,
        FirewallConstants.DECISION_REDACT: FirewallConstants.EVENT_REDACTED,
        FirewallConstants.DECISION_WARN: FirewallConstants.EVENT_WARNED,
        FirewallConstants.DECISION_ALLOW: FirewallConstants.EVENT_PROCESSED,
    }
    event_type = event_type_mapping.get(rule_result["action"], FirewallConstants.EVENT_PROCESSED)

    # Redact for logs as well
    redacted_prompt_for_logs = detector.redact_text(prompt, detection_result["risks"], redact_all_pii=True)

    # Persist log entry
    log_data = {
        DatabaseConstants.PROMPT_ID_FIELD: prompt_id,
        DatabaseConstants.EVENT_TYPE_FIELD: event_type,
        DatabaseConstants.DETAILS_FIELD: {
            DatabaseConstants.PROMPT_FIELD: redacted_prompt_for_logs,
            DatabaseConstants.REASON_FIELD: rule_result["reason"],
            DatabaseConstants.RISKS_DETECTED_FIELD: len(detection_result["risks"]),
            DatabaseConstants.RULES_APPLIED_FIELD: len(rule_result["applied_rules"]),
        },
        DatabaseConstants.USER_ID_FIELD: user_id or "",
        DatabaseConstants.METADATA_FIELD: metadata or {},
        DatabaseConstants.SEVERITY_FIELD: detection_result.get("severity", FirewallConstants.SEVERITY_LOW),
        DatabaseConstants.RISK_CATEGORIES_FIELD: detection_result.get("detected_categories", []),
    }
    log_store.save(tenant_id, log_data)

    # Build response payload
    return {
        "decision": rule_result["action"],
        "promptModified": rule_result["modified"],
        "risks": detection_result["risks"],
        "prompt_id": prompt_id,
        "timestamp": rule_result["timestamp"],
        "anomaly_score": detection_result["anomaly_score"],
        "confidence": detection_result["confidence"],
        "reason": rule_result["reason"],
        "applied_rules": rule_result["applied_rules"],
        "severity": detection_result.get("severity", FirewallConstants.SEVERITY_LOW),
        "risk_categories": detection_result.get("detected_categories", []),
        "prompt": prompt,
    }


