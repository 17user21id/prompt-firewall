"""
Regular expression patterns for Prompt Firewall MVP.
"""

class RegexConstants:
    """Regular expression patterns for all detection categories."""
    
    # ========== TENANT SANITIZATION ==========
    TENANT_ID_SANITIZE_PATTERN = r'[^a-zA-Z0-9\-_]'
    
    # ========== PII PATTERNS ==========
    # Email
    EMAIL_PATTERN = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    
    # SSN
    SSN_PATTERN = r'\b\d{3}-\d{2}-\d{4}\b'
    SSN_PATTERN_VARIANT = r'\b\d{3}-?\d{2}-?\d{4}\b'
    SSN_NUMBER_PATTERN = r'SSN\s*:?\s*\d{3}-?\d{2}-?\d{4}'
    
    # Phone
    PHONE_PATTERN = r'\b\d{3}-\d{3}-\d{4}\b|\b\(\d{3}\)\s*\d{3}-\d{4}\b'
    PHONE_PATTERN_ENHANCED = r'\b(?:\+?1[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})\b'
    
    # Credit Card
    CREDIT_CARD_PATTERN = r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b'
    CREDIT_CARD_PATTERN_VARIANT = r'\b(?:\d{4}[-\s]?){3}\d{4}\b'
    
    # IP Address
    IP_ADDRESS_PATTERN = r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b'
    IP_ADDRESS_PATTERN_ENHANCED = r'\b(?:\d{1,3}\.){3}\d{1,3}\b'
    
    # URL
    URL_PATTERN = r'https?://[^\s]+'
    
    # Address
    ADDRESS_FULL_PATTERN = r'\bAddress\s*:?\s*\d+\s+[A-Za-z\s]+(?:Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Drive|Dr|Lane|Ln|Way|Court|Ct),\s+[A-Za-z\s]+,\s+[A-Z]{2}\s+\d{5}\b'
    ADDRESS_SIMPLE_PATTERN = r'\b(?:Address|Send)\s*:?\s*\d+\s+[A-Za-z\s]+\b'
    ADDRESS_WITH_ZIP_PATTERN = r'\b\d+\s+[A-Za-z\s]+,?\s+[A-Za-z\s]+,?\s+(?:USA|United States|US)\s+\d{5}\b'
    
    # Date of Birth
    DATE_OF_BIRTH_PATTERN = r'\b(0[1-9]|1[0-2])[/-](0[1-9]|[12][0-9]|3[01])[/-](19|20)\d{2}\b|\b(19|20)\d{2}[/-](0[1-9]|1[0-2])[/-](0[1-9]|[12][0-9]|3[01])\b'
    BIRTHDAY_PATTERN = r'birthday\s+is\s+([0-9]{1,2}[/-][0-9]{1,2}[/-][0-9]{4})'
    
    # Passport
    PASSPORT_PATTERN = r'\b[Pp]assport\s+[Nn]umber\s*:?\s*[A-Z0-9]{8,}\b|\b[A-Z]{2}\s*\d{7,}\b'
    
    # Driver License
    DRIVER_LICENSE_PATTERN = r'\b[Dd]river[\s]?[Ss]?[\s]?[Ll]icense\s*:?\s*DL[-]?\d{8,}\b|DL[-]?\d{8,}'
    
    # UK Postcode
    UK_POSTCODE_PATTERN = r'\b[A-Z]{1,2}\d{1,2}[A-Z]?\s?\d[A-Z]{2}\b'
    
    # Bank Account
    BANK_ACCOUNT_PATTERN = r'\b[Bb]ank\s+[Aa]ccount\s*:?\s*\d{6,}\b'
    BANK_ACCOUNT_WITH_ROUTING_PATTERN = r'\b[Bb]ank\s+[Aa]ccount\s*:?\s*\d{6,}\s*,\s*[Rr]outing\s+\d{9}\b'
    
    # Routing Number
    ROUTING_NUMBER_PATTERN = r'\b[Rr]outing\s*:?\s*(?:0[2-6]\d{6}|0[89]\d{6}|[1-9]\d{8})\b'
    
    # CVV
    CVV_PATTERN = r'\b(?:cvv|cvc|security code).*?\d{3,4}\b'
    
    # Financial Transaction
    FINANCIAL_TRANSACTION_PATTERN = r'\b(?:transfer|withdraw|deposit).*?\$\d+[,\d]*\.?\d*\b'
    
    # ========== PHI PATTERNS ==========
    MEDICAL_RECORD_ID_PATTERN = r'\b(?:patient|medical|health).*?[Ii][Dd][\s:](?:MC-)?[\dA-Z-]{6,}\b'
    MEDICAL_CONDITION_PATTERN = r'\b(?:diagnosed|diagnosis|suffering|patient).*?(?:COVID|diabetes|HIV|hypertension|cancer)'
    HEALTH_DATA_PATTERN = r'\b(?:cholesterol|blood pressure|glucose|BP|HBA1C|level).*?\d+.*?(?:mg/dL|mmHg|mg/dl)\b'
    PRESCRIPTION_INFO_PATTERN = r'\b(?:prescription|medication|prescribed|dosage).*?\d+\s*(?:mg|unit|tablet|pill)'
    MEDICAL_PROCEDURE_PATTERN = r'\b(?:surgery|procedure|operation|treatment).*?(?:planned|scheduled|performed)'
    HEALTHCARE_FACILITY_PATTERN = r'\b(?:hospital|clinic|medical center|physician).*?\b'
    HEALTH_RECORD_PATTERN = r'[Hh]ealth\s+[Rr]ecord\s*:.*?(?:diagnosed|diagnosis).*?\d{4}-\d{2}-\d{2}'
    PHI_MARKER_PATTERN = r'\bPHI\s*:.*?(?:cholesterol|level|mg/dL)'
    DIAGNOSIS_DATE_PATTERN = r'(?:diagnosed|diagnosis).*?(?:on|with).*?\d{4}-\d{2}-\d{2}'
    MEDICAL_CARD_PATTERN = r'\b(?:medical|patient).*?card.*?[Ii][Dd]\s*:?\s*(?:MC-)?[\dA-Z-]{6,}\b'
    DISEASE_NAME_CONTEXT_PATTERN = r'\b(?:patient|diagnosed|suffering).*?(?:HIV|AIDS|COVID).*?(?:suggest|treatment|advice)\b'
    MEDICAL_RECORD_GENERAL_PATTERN = r'\b(?:patient|medical|diagnosis|treatment|prescription|doctor|physician|medical|health|disease|illness|symptom)\b'
    
    # ========== PROMPT INJECTION PATTERNS ==========
    INJECTION_IGNORE_INSTRUCTIONS = r'(ignore|forget|disregard|stop being).*(previous|prior|instructions|rules|guidelines|directives|helpful|ethics)'
    INJECTION_ROLEPLAY_ATTEMPT = r'(you are|act as|pretend to be|roleplay|simulate|imitate|pretend you are not).*(human|person|user|individual|filtered)'
    INJECTION_OVERRIDE_INSTRUCTIONS = r'(new instructions|updated instructions|revised instructions|change instructions|override)'
    INJECTION_TIME_OVERRIDE = r'(from now on|starting now|beginning now|from this point)'
    INJECTION_JAILBREAK = r'(jailbreak|dan|developer mode|admin|root|bypass)'
    INJECTION_SECRET_EXTRACTION = r'(confidential|secret|private|internal|reveal|show|tell|extract|print).*(password|key|api|credential|secrets|API keys|training data|configuration|environment variables|databases|logs|master key|source code|backend architecture|conversation|metadata)'
    INJECTION_SYSTEM_PROMPT_EXTRACTION = r'(what is your system prompt|initial system prompt|system instructions|reveal.*prompt)'
    INJECTION_SAFETY_OVERRIDE = r'(ignore safety|bypass safety|disable safety|override.*safety|harmful content|illegal advice|explicit content|restricted topics)'
    INJECTION_COMMAND_INJECTION = r'/\w+\s+(ignore|bypass|override).*'
    INJECTION_CONDITIONAL_INJECTION = r'(if i say|trick: if|if|please).*(ignore|forget|disregard|bypass)'
    INJECTION_REPETITIVE_REQUEST = r'repeat.*?\d+\s+times'
    INJECTION_ASSUME_NO_RULES = r'assume no rules|forget guidelines|no restrictions|respond freely'
    INJECTION_TRUTH_TELLING = r'answer truthfully|respond truthfully|be honest about'
