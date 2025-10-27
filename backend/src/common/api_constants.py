"""
API-related constants for Prompt Firewall MVP.
"""

class ApiConstants:
    """API-related constants."""
    
    # HTTP Status Codes
    HTTP_200_OK = 200
    HTTP_400_BAD_REQUEST = 400
    HTTP_401_UNAUTHORIZED = 401
    HTTP_403_FORBIDDEN = 403
    HTTP_404_NOT_FOUND = 404
    HTTP_429_TOO_MANY_REQUESTS = 429
    HTTP_500_INTERNAL_SERVER_ERROR = 500
    
    # API Endpoints
    TENANTS_ENDPOINT = "/v1/tenants"
    TENANTS_LOGIN_ENDPOINT = "/v1/tenants/login"
    TENANTS_STATS_ENDPOINT = "/v1/tenants/{tenant_id}/stats"
    QUERY_ENDPOINT = "/v1/query"
    RULES_ENDPOINT = "/v1/rules"
    RULES_STATS_ENDPOINT = "/v1/rules/stats"
    LOGS_ENDPOINT = "/v1/logs"
    LOGS_STATS_ENDPOINT = "/v1/logs/stats"
    LOGS_EXPORT_ENDPOINT = "/v1/logs/export"
    PROMPTS_ENDPOINT = "/v1/prompts"
    PROMPTS_STATS_ENDPOINT = "/v1/prompts/stats"
    STATS_ENDPOINT = "/v1/stats"
    ADMIN_TENANTS_ENDPOINT = "/v1/admin/tenants"
    
    # Error Messages
    FAILED_TO_CREATE_TENANT = "Failed to create tenant: {}"
    FAILED_TO_PROCESS_PROMPT = "Failed to process prompt: {}"
    FAILED_TO_CREATE_RULE = "Failed to create rule: {}"
    FAILED_TO_UPDATE_RULE = "Failed to update rule: {}"
    FAILED_TO_DELETE_RULE = "Failed to delete rule: {}"
    FAILED_TO_GET_PATTERNS = "Failed to get patterns: {}"
    LOGIN_FAILED = "Login failed: {}"
    
    # Success Messages
    TENANT_CREATED_SUCCESSFULLY = "Tenant created successfully: {}"
    RULE_DELETED_SUCCESSFULLY = "Rule deleted successfully"
    LOGIN_SUCCESSFUL = "Login successful. Use the API key for bearer token authentication."
    
    # Validation Messages
    DUPLICATE_TENANT_NAME = "Tenant name '{}' already exists. Please choose a different name."
    INVALID_TENANT_CREDENTIALS = "Invalid tenant name or password. Please check your credentials and try again."
    INVALID_RULE = "Invalid rule: {}"
    RULE_NOT_FOUND = "Rule not found"
    PROMPT_NOT_FOUND = "Prompt not found"
    
    # Feature Messages
    LOG_EXPORT_COMING_SOON = "Log export feature coming soon"
    
    # Health Check
    HEALTH_STATUS = "healthy"
    FIRESTORE_STATUS = "connected"
    DETECTOR_STATUS = "active"
    RULES_ENGINE_STATUS = "active"
    INTERNAL_SERVER_ERROR = "Internal Server Error"
