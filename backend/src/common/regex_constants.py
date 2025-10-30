"""
Regular expression patterns for Prompt Firewall MVP.
"""

class RegexConstants:
    """Regular expression patterns for all detection categories."""
    
    # ========== TENANT SANITIZATION ==========
    TENANT_ID_SANITIZE_PATTERN = r'[^a-zA-Z0-9\-_]'
    
    # ========== PII/NETWORK PATTERNS (only those still referenced) ==========
    EMAIL_PATTERN = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    SSN_PATTERN_VARIANT = r'\b\d{3}-?\d{2}-?\d{4}\b'
    PHONE_PATTERN_ENHANCED = r'\b(?:\+?1[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})\b'
    CREDIT_CARD_PATTERN_VARIANT = r'\b(?:\d{4}[-\s]?){3}\d{4}\b'
    IP_ADDRESS_PATTERN_ENHANCED = r'\b(?:\d{1,3}\.){3}\d{1,3}\b'
    URL_PATTERN = r'https?://[^\s]+'

