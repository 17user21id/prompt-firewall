"""
Application-level constants for Prompt Firewall MVP.
"""

class AppConstants:
    """Application-level constants."""
    
    # Application Info
    APP_NAME = "Prompt Firewall API"
    APP_DESCRIPTION = "AI Security Firewall for detecting PII and prompt injection attempts"
    APP_VERSION = "1.0.0"
    
    # API Endpoints
    DOCS_URL = "/docs"
    REDOC_URL = "/redoc"
    HEALTH_ENDPOINT = "/health"
    
    # CORS Configuration
    CORS_ALLOW_ORIGINS = ["*"]  # Configure appropriately for production
    CORS_ALLOW_CREDENTIALS = True
    CORS_ALLOW_METHODS = ["*"]
    CORS_ALLOW_HEADERS = ["*"]
