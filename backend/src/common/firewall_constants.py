"""
Firewall-related constants for Prompt Firewall MVP.
"""

class FirewallConstants:
    """Firewall-related constants."""
    
    # Environment Variables
    OPENAI_API_KEY_ENV = "OPENAI_API_KEY"
    OPENAI_MODEL_ENV = "OPENAI_MODEL"
    
    # Default Values
    DEFAULT_OPENAI_MODEL = "gpt-4"
    
    # Decision Types
    DECISION_ALLOW = "allow"
    DECISION_BLOCK = "block"
    DECISION_REDACT = "redact"
    DECISION_WARN = "warn"
    
    # Risk Types
    RISK_TYPE_PII_EMAIL = "PII_EMAIL"
    RISK_TYPE_PII_SSN = "PII_SSN"
    RISK_TYPE_PII_PHONE = "PII_PHONE"
    RISK_TYPE_PII_CREDIT_CARD = "PII_CREDIT_CARD"
    RISK_TYPE_PII_IP_ADDRESS = "PII_IP_ADDRESS"
    RISK_TYPE_PII_URL = "PII_URL"
    RISK_TYPE_PII_MEDICAL_RECORD = "PII_MEDICAL_RECORD"
    RISK_TYPE_INJECTION = "INJECTION"
    RISK_TYPE_INJECTION_OPENAI = "INJECTION_OPENAI"
    RISK_TYPE_CUSTOM = "CUSTOM"
    
    # Severity Levels
    SEVERITY_LOW = "low"
    SEVERITY_MEDIUM = "medium"
    SEVERITY_HIGH = "high"
    SEVERITY_CRITICAL = "critical"
    
    # Event Types
    EVENT_PROCESSED = "processed"
    EVENT_BLOCKED = "blocked"
    EVENT_REDACTED = "redacted"
    EVENT_WARNED = "warned"
    EVENT_ERROR = "error"
    EVENT_RULE_CREATED = "rule_created"
    EVENT_RULE_UPDATED = "rule_updated"
    EVENT_RULE_DELETED = "rule_deleted"
    EVENT_TENANT_CREATED = "tenant_created"
    EVENT_TENANT_UPDATED = "tenant_updated"
    EVENT_TENANT_LOGIN = "tenant_login"
