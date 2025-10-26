"""
Authentication-related constants for Prompt Firewall MVP.
"""

class AuthConstants:
    """Authentication-related constants."""
    
    # Environment Variables
    ENCRYPTION_KEY_ENV = "ENCRYPTION_KEY"
    JWT_SECRET_ENV = "JWT_SECRET"
    JWT_ALGORITHM_ENV = "JWT_ALGORITHM"
    JWT_EXPIRY_HOURS_ENV = "JWT_EXPIRY_HOURS"
    
    # Default Values
    DEFAULT_JWT_SECRET = "your-secret-key-change-in-production"
    DEFAULT_JWT_ALGORITHM = "HS256"
    DEFAULT_JWT_EXPIRY_HOURS = 24
    
    # API Key Configuration
    API_KEY_LENGTH = 32
    API_KEY_MIN_LENGTH = 10
    TENANT_ID_MAX_LENGTH = 50
    
    # Rate Limiting
    DEFAULT_MAX_REQUESTS = 100
    DEFAULT_WINDOW_MINUTES = 1
    
    # Token Format
    TOKEN_SEPARATOR = ":"
    BEARER_PREFIX = "Bearer"
    
    # Error Messages
    INVALID_AUTH_CREDENTIALS = "Invalid authentication credentials. Expected format: tenant_id:api_key"
    ACCESS_DENIED_INVALID_TENANT = "Access denied: Invalid tenant"
    TENANT_NOT_FOUND = "Tenant not found"
    INVALID_ADMIN_CREDENTIALS = "Invalid admin credentials"
    RATE_LIMIT_EXCEEDED = "Rate limit exceeded"
    
    # Success Messages
    AUTH_MANAGER_INITIALIZED = "AuthManager initialized"
    
    # Warning Messages
    ENCRYPTION_KEY_WARNING = "WARNING: Generated new encryption key. Set ENCRYPTION_KEY={} in environment"
    
    # Log Messages
    VALIDATING_CREDENTIALS = "Validating credentials for tenant: {}"
    TENANT_NOT_FOUND_LOG = "Tenant not found: {}"
    INVALID_PASSWORD_LOG = "Invalid password for tenant: {}"
    SUCCESSFUL_LOGIN_LOG = "Successful login for tenant: {}"
    ERROR_VALIDATING_CREDENTIALS = "Error validating tenant credentials for {}: {}"
    ERROR_CHECKING_TENANT_NAME = "Error checking tenant name: {}"
    ERROR_VALIDATING_API_KEY = "Error validating API key: {}"
    ERROR_VERIFYING_PASSWORD = "Error verifying password: {}"
    ERROR_ENCRYPTING_API_KEY = "Error encrypting API key: {}"
    ERROR_DECRYPTING_API_KEY = "Error decrypting API key: {}"
    
    # Security Messages
    SECURITY_EVENT_PREFIX = "Security event: {}"
    AUTHENTICATION_EVENT_PREFIX = "Authentication event: {}"
    API_REQUEST_PREFIX = "API Request: {} {}"
    PERFORMANCE_PREFIX = "Performance: {} completed in {:.3f}s"
    DATABASE_OPERATION_PREFIX = "Database {}: {}"
