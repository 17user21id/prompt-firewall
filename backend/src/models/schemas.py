"""
Pydantic models for data validation and serialization.
"""

from pydantic import BaseModel, Field, validator
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum

class SeverityLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class ActionType(str, Enum):
    BLOCK = "block"
    REDACT = "redact"
    WARN = "warn"
    ALLOW = "allow"

class RiskType(str, Enum):
    PII_EMAIL = "PII_EMAIL"
    PII_SSN = "PII_SSN"
    PII_PHONE = "PII_PHONE"
    PII_CREDIT_CARD = "PII_CREDIT_CARD"
    PII_IP_ADDRESS = "PII_IP_ADDRESS"
    PII_URL = "PII_URL"
    PII_MEDICAL_RECORD = "PII_MEDICAL_RECORD"
    INJECTION = "INJECTION"
    INJECTION_OPENAI = "INJECTION_OPENAI"
    CUSTOM = "CUSTOM"

class EventType(str, Enum):
    PROCESSED = "processed"
    BLOCKED = "blocked"
    REDACTED = "redacted"
    WARNED = "warned"
    ERROR = "error"
    RULE_CREATED = "rule_created"
    RULE_UPDATED = "rule_updated"
    RULE_DELETED = "rule_deleted"
    TENANT_CREATED = "tenant_created"
    TENANT_UPDATED = "tenant_updated"

class Risk(BaseModel):
    """Model for detected risks."""
    type: RiskType
    match: str
    start: Optional[int] = None
    end: Optional[int] = None
    severity: SeverityLevel
    action: ActionType
    confidence: float = Field(ge=0.0, le=1.0)
    score: Optional[float] = None
    reasoning: Optional[str] = None
    rule_id: Optional[str] = None

class TenantCreate(BaseModel):
    """Model for creating a new tenant."""
    name: str = Field(..., min_length=1, max_length=100)
    password: str = Field(..., min_length=8, max_length=128)
    metadata: Optional[Dict[str, Any]] = {}

class TenantLogin(BaseModel):
    """Model for tenant login."""
    name: str = Field(..., min_length=1, max_length=100)
    password: str = Field(..., min_length=1)

class TenantLoginResponse(BaseModel):
    """Model for tenant login response."""
    tenant_id: str
    name: str
    api_key: str
    message: str
    status: str = "success"

class TenantResponse(BaseModel):
    """Model for tenant response."""
    tenant_id: str
    name: str
    api_key: str
    created_at: str
    updated_at: str
    status: str = "active"
    metadata: Dict[str, Any] = {}

class TenantStats(BaseModel):
    """Model for tenant statistics."""
    tenant_id: str
    name: str
    created_at: str
    prompts_count: int
    rules_count: int
    logs_count: int
    status: str

class QueryRequest(BaseModel):
    """Model for query request."""
    tenant_id: str
    prompt: str = Field(..., min_length=1, max_length=10000)
    user_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = {}

class QueryResponse(BaseModel):
    """Model for query response."""
    decision: ActionType
    promptModified: str
    risks: List[Risk]
    prompt_id: str
    timestamp: str
    anomaly_score: float = Field(ge=0.0, le=1.0)
    confidence: float = Field(ge=0.0, le=1.0)
    reason: str
    applied_rules: List[Dict[str, Any]] = []
    severity: Optional[str] = "low"
    risk_categories: Optional[List[str]] = []
    prompt: Optional[str] = ""

class RuleCreate(BaseModel):
    """Model for creating a new rule."""
    type: str = Field(..., min_length=1, max_length=50)
    pattern: str = Field(..., min_length=1, max_length=1000)
    action: ActionType
    severity: SeverityLevel
    description: Optional[str] = Field(None, max_length=500)
    enabled: bool = True
    metadata: Optional[Dict[str, Any]] = {}

    @validator('pattern')
    def validate_pattern(cls, v):
        import re
        try:
            re.compile(v)
            return v
        except re.error as e:
            raise ValueError(f"Invalid regex pattern: {e}")

class RuleUpdate(BaseModel):
    """Model for updating a rule."""
    type: Optional[str] = Field(None, min_length=1, max_length=50)
    pattern: Optional[str] = Field(None, min_length=1, max_length=1000)
    action: Optional[ActionType] = None
    severity: Optional[SeverityLevel] = None
    description: Optional[str] = Field(None, max_length=500)
    enabled: Optional[bool] = None
    metadata: Optional[Dict[str, Any]] = None

    @validator('pattern')
    def validate_pattern(cls, v):
        if v is not None:
            import re
            try:
                re.compile(v)
                return v
            except re.error as e:
                raise ValueError(f"Invalid regex pattern: {e}")
        return v

class RuleResponse(BaseModel):
    """Model for rule response."""
    rule_id: str
    type: str
    pattern: str
    action: ActionType
    severity: SeverityLevel
    version: int
    created_at: str
    updated_at: str
    enabled: bool
    description: str
    metadata: Dict[str, Any] = {}

class RuleStats(BaseModel):
    """Model for rule statistics."""
    total_rules: int
    active_rules: int
    inactive_rules: int
    pii_rules: int
    injection_rules: int
    block_rules: int
    redact_rules: int
    warn_rules: int
    high_severity_rules: int
    medium_severity_rules: int
    low_severity_rules: int

class LogCreate(BaseModel):
    """Model for creating a log entry."""
    prompt_id: str
    event_type: EventType
    details: Dict[str, Any] = {}
    user_id: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = {}

class LogResponse(BaseModel):
    """Model for log response."""
    log_id: str
    prompt_id: str
    event_type: EventType
    details: Dict[str, Any]
    timestamp: str
    user_id: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    metadata: Dict[str, Any] = {}
    severity: Optional[str] = None
    risk_categories: Optional[List[str]] = None

class LogStats(BaseModel):
    """Model for log statistics."""
    total_logs: int
    processed_logs: int
    blocked_logs: int
    redacted_logs: int
    warned_logs: int
    error_logs: int
    unique_users: int
    unique_ips: int
    daily_counts: Dict[str, int] = {}
    event_type_counts: Dict[str, int] = {}

class PromptResponse(BaseModel):
    """Model for prompt response."""
    prompt_id: str
    prompt: str
    response: str
    decision: ActionType
    promptModified: str
    risks: List[Risk]
    anomaly_score: float = Field(ge=0.0, le=1.0)
    timestamp: str
    user_id: Optional[str] = None
    metadata: Dict[str, Any] = {}

class PromptStats(BaseModel):
    """Model for prompt statistics."""
    total_prompts: int
    blocked_prompts: int
    redacted_prompts: int
    warned_prompts: int
    allowed_prompts: int
    pii_detections: int
    injection_detections: int
    avg_anomaly_score: float = Field(ge=0.0, le=1.0)

class LogsQueryRequest(BaseModel):
    """Model for logs query request."""
    tenant_id: str
    event_type: Optional[EventType] = None
    date_from: Optional[str] = None
    date_to: Optional[str] = None
    user_id: Optional[str] = None
    prompt_id: Optional[str] = None
    limit: int = Field(default=100, ge=1, le=1000)

class PromptsQueryRequest(BaseModel):
    """Model for prompts query request."""
    tenant_id: str
    decision: Optional[ActionType] = None
    date_from: Optional[str] = None
    date_to: Optional[str] = None
    user_id: Optional[str] = None
    has_risks: Optional[bool] = None
    limit: int = Field(default=100, ge=1, le=1000)

class RulesQueryRequest(BaseModel):
    """Model for rules query request."""
    tenant_id: str
    type: Optional[str] = None
    action: Optional[ActionType] = None
    severity: Optional[SeverityLevel] = None
    enabled: Optional[bool] = None
    limit: int = Field(default=100, ge=1, le=1000)

class BulkRuleUpdate(BaseModel):
    """Model for bulk rule updates."""
    updates: List[Dict[str, Any]] = Field(..., min_items=1, max_items=100)

class ErrorResponse(BaseModel):
    """Model for error responses."""
    error: str
    message: str
    details: Optional[Dict[str, Any]] = None
    timestamp: str

class HealthResponse(BaseModel):
    """Model for health check response."""
    status: str
    timestamp: str
    version: str
    services: Dict[str, str] = {}

class StatsResponse(BaseModel):
    """Model for statistics response."""
    tenant_stats: Optional[TenantStats] = None
    prompt_stats: Optional[PromptStats] = None
    rule_stats: Optional[RuleStats] = None
    log_stats: Optional[LogStats] = None
    timestamp: str
