"""
Database-related constants for Prompt Firewall MVP.
"""

class DatabaseConstants:
    """Database-related constants."""
    
    # Collections
    TENANTS_COLLECTION = "tenants"
    PROMPTS_COLLECTION = "prompts"
    RULES_COLLECTION = "rules"
    LOGS_COLLECTION = "logs"
    
    # Field Names
    TENANT_ID_FIELD = "tenant_id"
    NAME_FIELD = "name"
    PASSWORD_FIELD = "password"
    API_KEY_FIELD = "api_key"
    CREATED_AT_FIELD = "created_at"
    UPDATED_AT_FIELD = "updated_at"
    STATUS_FIELD = "status"
    METADATA_FIELD = "metadata"
    
    # Log/Prompt Field Names
    EVENT_TYPE_FIELD = "event_type"
    PROMPT_ID_FIELD = "prompt_id"
    USER_ID_FIELD = "user_id"
    DETAILS_FIELD = "details"
    PROMPT_FIELD = "prompt"
    CATEGORY_FIELD = "category"
    TYPE_FIELD = "type"
    RISKS_FIELD = "risks"
    START_DATE_FIELD = "start_date"
    END_DATE_FIELD = "end_date"
    SEVERITY_FIELD = "severity"
    HAS_RISKS_FIELD = "has_risks"
    DECISION_FIELD = "decision"
    ANOMALY_SCORE_FIELD = "anomaly_score"
    RESPONSE_FIELD = "response"
    PROMPT_MODIFIED_FIELD = "promptModified"
    
    # Rule Field Names
    TYPE_FIELD = "type"
    ACTION_FIELD = "action"
    ENABLED_FIELD = "enabled"
    PATTERN_ID_FIELD = "pattern_id"
    DESCRIPTION_FIELD = "description"
    SOURCE_FIELD = "source"
    CONFIDENCE_FIELD = "confidence"
    
    # Value Constants
    BUILT_IN_SOURCE = "built-in"
    CUSTOM_SOURCE = "custom"
    PASSWORD_LOGIN_METHOD = "password"
    SUCCESS_STATUS = "success"
    SYSTEM_CREATED_BY = "system"
    
    # Log/Event Metadata Field Names
    RULE_ID_FIELD = "rule_id"
    RULE_TYPE_FIELD = "rule_type"
    TENANT_NAME_FIELD = "tenant_name"
    CREATED_BY_FIELD = "created_by"
    UPDATED_FIELDS_FIELD = "updated_fields"
    REASON_FIELD = "reason"
    RISKS_DETECTED_FIELD = "risks_detected"
    RULES_APPLIED_FIELD = "rules_applied"
    RISK_CATEGORIES_FIELD = "risk_categories"
    LOGIN_METHOD_FIELD = "login_method"
    
    # Response Payload Field Names
    MESSAGE_FIELD = "message"
    BUILT_IN_PATTERNS_FIELD = "built_in_patterns"
    CUSTOM_RULES_FIELD = "custom_rules"
    TOTAL_BUILT_IN_FIELD = "total_built_in"
    TOTAL_CUSTOM_FIELD = "total_custom"
    TOTAL_ACTIVE_FIELD = "total_active"
    PATTERN_VALUE_FIELD = "pattern"
    
    # Service Names
    FIRESTORE_SERVICE = "firestore"
    DETECTOR_SERVICE = "detector"
    RULES_ENGINE_SERVICE = "rules_engine"
    
    # Default Values
    DEFAULT_STATUS = "active"
    DEFAULT_METADATA = {}
    
    # Environment Variables
    GOOGLE_APPLICATION_CREDENTIALS_ENV = "GOOGLE_APPLICATION_CREDENTIALS"
    GOOGLE_CLOUD_PROJECT_ENV = "GOOGLE_CLOUD_PROJECT"
    FIRESTORE_DATABASE_ENV = "FIRESTORE_DATABASE"
