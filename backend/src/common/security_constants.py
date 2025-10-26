"""
Security-related constants for Prompt Firewall MVP.
"""

class SecurityConstants:
    """Security-related constants."""
    
    # Password Requirements
    MIN_PASSWORD_LENGTH = 8
    MAX_PASSWORD_LENGTH = 128
    
    # Encryption
    ENCRYPTION_ALGORITHM = "utf-8"
    BASE64_ENCODING = "utf-8"
    
    # Security Headers
    AUTHORIZATION_HEADER = "Authorization"
    CONTENT_TYPE_HEADER = "Content-Type"
    CONTENT_TYPE_JSON = "application/json"
