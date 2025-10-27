"""
Firewall-related constants for Prompt Firewall MVP.
"""

from enum import Enum

class SeverityLevel(Enum):
    """Severity levels for detected risks."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class ActionType(Enum):
    """Action types for firewall rules."""
    ALLOW = "allow"
    BLOCK = "block"
    REDACT = "redact"
    WARN = "warn"

class RiskCategoryType(Enum):
    """Risk category types."""
    PII = "PII"
    PHI = "PHI"
    PCI = "PCI"
    PROMPT_INJECTION = "PROMPT_INJECTION"
    CUSTOM = "CUSTOM"

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
    
    # Action Priority (for determining final action)
    ACTION_PRIORITY_BLOCK = 4
    ACTION_PRIORITY_REDACT = 3
    ACTION_PRIORITY_WARN = 2
    ACTION_PRIORITY_ALLOW = 1
    
    # Detection Thresholds
    INJECTION_DETECTION_THRESHOLD = 0.3
    INJECTION_SEVERE_THRESHOLD = 0.7
    INJECTION_MEDIUM_THRESHOLD = 0.5
    ANOMALY_LENGTH_THRESHOLD_LONG = 1000
    ANOMALY_LENGTH_THRESHOLD_SHORT = 10
    ANOMALY_REPETITION_THRESHOLD = 0.5
    
    # Default Confidence Values
    DEFAULT_CONFIDENCE_REGEX = 0.9
    DEFAULT_CONFIDENCE_CUSTOM = 0.8
    DEFAULT_CONFIDENCE_OPENAI = 0.5
    
    # Redaction Text
    REDACTED_TEXT = "[REDACTED]"
    
    # Risk Type Mapping Keys
    TYPE_MAPPING_PII = "PII"
    TYPE_MAPPING_PHI = "PHI"
    TYPE_MAPPING_PCI = "PCI"
    TYPE_MAPPING_CUSTOM = "CUSTOM"
    TYPE_MAPPING_INJECTION = "INJECTION"
    
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
