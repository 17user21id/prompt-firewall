"""
Regular expression patterns for Prompt Firewall MVP.
"""

class RegexConstants:
    """Regular expression patterns."""
    
    # Tenant ID sanitization
    TENANT_ID_SANITIZE_PATTERN = r'[^a-zA-Z0-9\-_]'
    
    # PII Patterns (examples - these would be in the detector)
    EMAIL_PATTERN = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    SSN_PATTERN = r'\b\d{3}-\d{2}-\d{4}\b'
    PHONE_PATTERN = r'\b\d{3}-\d{3}-\d{4}\b|\b\(\d{3}\)\s*\d{3}-\d{4}\b'
    CREDIT_CARD_PATTERN = r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b'
    IP_ADDRESS_PATTERN = r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b'
    URL_PATTERN = r'https?://[^\s]+'
