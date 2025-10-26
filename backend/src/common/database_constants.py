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
    
    # Default Values
    DEFAULT_STATUS = "active"
    DEFAULT_METADATA = {}
    
    # Environment Variables
    GOOGLE_APPLICATION_CREDENTIALS_ENV = "GOOGLE_APPLICATION_CREDENTIALS"
    GOOGLE_CLOUD_PROJECT_ENV = "GOOGLE_CLOUD_PROJECT"
    FIRESTORE_DATABASE_ENV = "FIRESTORE_DATABASE"
