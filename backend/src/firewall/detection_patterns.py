"""
Detection Patterns for all security categories: PII, PHI, PCI, Prompt Injection
Provides modular, generic pattern detection
"""

import re
from typing import List, Dict, Any, Tuple
from enum import Enum

class RiskCategory(Enum):
    """Risk categories"""
    PROMPT_INJECTION = "PROMPT_INJECTION"
    PII = "PII"
    PHI = "PHI"
    PCI = "PCI"

class DetectionPattern:
    """A single detection pattern"""
    def __init__(self, name: str, pattern: str, category: RiskCategory, 
                 severity: str, action: str, confidence: float = 0.9,
                 description: str = None):
        self.name = name
        self.pattern = re.compile(pattern, re.IGNORECASE)
        self.category = category
        self.severity = severity
        self.action = action
        self.confidence = confidence
        self.description = description or name

    def detect(self, text: str) -> List[Dict[str, Any]]:
        """Detect this pattern in text"""
        matches = []
        
        # Map category to specific risk type based on context
        risk_type_map = {
            "PROMPT_INJECTION": "INJECTION",
            "PII": "CUSTOM",  # Will be mapped to specific PII types in the detector
            "PHI": "CUSTOM",
            "PCI": "CUSTOM"
        }
        
        # Map severity to valid enum values
        severity_map = {
            "critical": "high",
            "high": "high",
            "medium": "medium",
            "low": "low"
        }
        
        for match in self.pattern.finditer(text):
            # Get mapped risk type
            risk_type = risk_type_map.get(self.category.value, self.category.value)
            
            # Get mapped severity
            mapped_severity = severity_map.get(self.severity, self.severity)
            
            matches.append({
                "type": risk_type,
                "category": self.category.value,
                "subtype": self.name,
                "match": match.group(),
                "start": match.start(),
                "end": match.end(),
                "severity": mapped_severity,
                "action": self.action,
                "confidence": self.confidence,
                "description": self.description
            })
        return matches


class DetectionPatternRegistry:
    """Registry of all detection patterns"""
    
    # Prompt Injection Patterns
    PROMPT_INJECTION_PATTERNS = [
        DetectionPattern(
            "ignore_instructions", 
            r"(ignore|forget|disregard|stop being).*(previous|prior|instructions|rules|guidelines|directives|helpful|ethics)",
            RiskCategory.PROMPT_INJECTION, "high", "block", 0.9,
            "Attempt to ignore system instructions"
        ),
        DetectionPattern(
            "roleplay_attempt",
            r"(you are|act as|pretend to be|roleplay|simulate|imitate|pretend you're not).*(human|person|user|individual|filtered)",
            RiskCategory.PROMPT_INJECTION, "high", "block", 0.85,
            "Attempt to roleplay or impersonate"
        ),
        DetectionPattern(
            "override_instructions",
            r"(new instructions|updated instructions|revised instructions|change instructions|override)",
            RiskCategory.PROMPT_INJECTION, "high", "block", 0.9,
            "Attempt to override system instructions"
        ),
        DetectionPattern(
            "time_override",
            r"(from now on|starting now|beginning now|from this point)",
            RiskCategory.PROMPT_INJECTION, "high", "block", 0.85,
            "Attempt to change AI behavior from a specific time"
        ),
        DetectionPattern(
            "jailbreak_attempt",
            r"(jailbreak|dan|developer mode|admin|root|bypass)",
            RiskCategory.PROMPT_INJECTION, "high", "block", 0.9,
            "Attempt to jailbreak or bypass safety measures"
        ),
        DetectionPattern(
            "secret_extraction",
            r"(confidential|secret|private|internal|reveal|show|tell|extract|print).*(password|key|api|credential|secrets|API keys|training data|configuration|environment variables|databases|logs|master key|source code|backend architecture|conversation|metadata)",
            RiskCategory.PROMPT_INJECTION, "critical", "block", 0.95,
            "Attempt to extract secrets or credentials"
        ),
        DetectionPattern(
            "system_prompt_extraction",
            r"(what is your system prompt|initial system prompt|system instructions|reveal.*prompt)",
            RiskCategory.PROMPT_INJECTION, "high", "block", 0.9,
            "Attempt to extract system prompts"
        ),
        DetectionPattern(
            "safety_override",
            r"(ignore safety|bypass safety|disable safety|override.*safety|harmful content|illegal advice|explicit content|restricted topics)",
            RiskCategory.PROMPT_INJECTION, "critical", "block", 0.95,
            "Attempt to override safety measures"
        ),
        DetectionPattern(
            "command_injection",
            r"/\w+\s+(ignore|bypass|override).*",
            RiskCategory.PROMPT_INJECTION, "critical", "block", 0.95,
            "Command-based injection attempt"
        ),
        DetectionPattern(
            "conditional_injection",
            r"(if i say|trick: if|if|please).*(ignore|forget|disregard|bypass)",
            RiskCategory.PROMPT_INJECTION, "critical", "block", 0.9,
            "Conditional injection attempt"
        ),
        DetectionPattern(
            "repetitive_request",
            r"repeat.*?\d+\s+times",
            RiskCategory.PROMPT_INJECTION, "medium", "warn", 0.7,
            "Repetitive request detected"
        ),
        DetectionPattern(
            "assume_no_rules",
            r"assume no rules|forget guidelines|no restrictions|respond freely",
            RiskCategory.PROMPT_INJECTION, "critical", "block", 0.95,
            "Attempt to assume no rules or restrictions"
        ),
        DetectionPattern(
            "truth_telling",
            r"answer truthfully|respond truthfully|be honest about",
            RiskCategory.PROMPT_INJECTION, "high", "block", 0.85,
            "Attempt to bypass filtering by requesting truth"
        ),
    ]

    # PII (Personally Identifiable Information) Patterns
    PII_PATTERNS = [
        DetectionPattern(
            "email",
            r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",
            RiskCategory.PII, "high", "redact", 0.95,
            "Email address detected"
        ),
        DetectionPattern(
            "phone_number",
            r"\b(?:\+?1[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})\b",
            RiskCategory.PII, "medium", "redact", 0.9,
            "Phone number detected"
        ),
        DetectionPattern(
            "ssn",
            r"\b\d{3}-?\d{2}-?\d{4}\b",
            RiskCategory.PII, "critical", "block", 0.95,
            "Social Security Number detected"
        ),
        DetectionPattern(
            "ip_address",
            r"\b(?:\d{1,3}\.){3}\d{1,3}\b",
            RiskCategory.PII, "medium", "warn", 0.85,
            "IP address detected"
        ),
        DetectionPattern(
            "url",
            r"https?://[^\s]+",
            RiskCategory.PII, "low", "warn", 0.8,
            "URL detected"
        ),
        DetectionPattern(
            "address",
            r"\bAddress\s*:?\s*\d+\s+[A-Za-z\s]+(?:Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Drive|Dr|Lane|Ln|Way|Court|Ct),\s+[A-Za-z\s]+,\s+[A-Z]{2}\s+\d{5}\b",
            RiskCategory.PII, "high", "redact", 0.9,
            "Physical address detected with full format"
        ),
        DetectionPattern(
            "simple_address",
            r"\b(?:Address|Send)\s*:?\s*\d+\s+[A-Za-z\s]+\b",
            RiskCategory.PII, "medium", "warn", 0.7,
            "Potential physical address detected"
        ),
        DetectionPattern(
            "address_with_zip",
            r"\b\d+\s+[A-Za-z\s]+,?\s+[A-Za-z\s]+,?\s+(?:USA|United States|US)\s+\d{5}\b",
            RiskCategory.PII, "high", "redact", 0.85,
            "Physical address with country and zip detected"
        ),
        DetectionPattern(
            "date_of_birth",
            r"\b(0[1-9]|1[0-2])[/-](0[1-9]|[12][0-9]|3[01])[/-](19|20)\d{2}\b|\b(19|20)\d{2}[/-](0[1-9]|1[0-2])[/-](0[1-9]|[12][0-9]|3[01])\b",
            RiskCategory.PII, "high", "redact", 0.85,
            "Date of birth detected"
        ),
        DetectionPattern(
            "birthday",
            r"birthday\s+is\s+([0-9]{1,2}[/-][0-9]{1,2}[/-][0-9]{4})",
            RiskCategory.PII, "high", "redact", 0.9,
            "Birthday detected"
        ),
        DetectionPattern(
            "passport",
            r"\b[Pp]assport\s+[Nn]umber\s*:?\s*[A-Z0-9]{8,}\b|\b[A-Z]{2}\s*\d{7,}\b",
            RiskCategory.PII, "critical", "block", 0.95,
            "Passport number detected"
        ),
        DetectionPattern(
            "driver_license",
            r"\b[Dd]river['\s]?[Ss]?['\s]?[Ll]icense\s*:?\s*DL[-]?\d{8,}\b|DL[-]?\d{8,}",
            RiskCategory.PII, "critical", "block", 0.95,
            "Driver's license detected"
        ),
        DetectionPattern(
            "uk_postcode",
            r"\b[A-Z]{1,2}\d{1,2}[A-Z]?\s?\d[A-Z]{2}\b",
            RiskCategory.PII, "high", "redact", 0.9,
            "UK postcode detected"
        ),
        DetectionPattern(
            "ssn_number",
            r"SSN\s*:?\s*\d{3}-?\d{2}-?\d{4}",
            RiskCategory.PII, "critical", "block", 0.95,
            "SSN number detected"
        ),
    ]

    # PHI (Protected Health Information) Patterns
    PHI_PATTERNS = [
        DetectionPattern(
            "medical_record_id",
            r"\b(?:patient|medical|health).*?[Ii][Dd][\s:](?:MC-)?[\dA-Z-]{6,}\b",
            RiskCategory.PHI, "critical", "block", 0.95,
            "Medical record ID detected"
        ),
        DetectionPattern(
            "medical_condition",
            r"\b(?:diagnosed|diagnosis|suffering|patient).*?(?:COVID|diabetes|HIV|hypertension|cancer)",
            RiskCategory.PHI, "critical", "block", 0.9,
            "Medical condition information detected"
        ),
        DetectionPattern(
            "health_data",
            r"\b(?:cholesterol|blood pressure|glucose|BP|HBA1C|level).*?\d+.*?(?:mg/dL|mmHg|mg/dl)\b",
            RiskCategory.PHI, "critical", "block", 0.9,
            "Health measurement data detected"
        ),
        DetectionPattern(
            "prescription_info",
            r"\b(?:prescription|medication|prescribed|dosage).*?\d+\s*(?:mg|unit|tablet|pill)",
            RiskCategory.PHI, "high", "redact", 0.9,
            "Prescription information detected"
        ),
        DetectionPattern(
            "medical_procedure",
            r"\b(?:surgery|procedure|operation|treatment).*?(?:planned|scheduled|performed)",
            RiskCategory.PHI, "high", "redact", 0.85,
            "Medical procedure information detected"
        ),
        DetectionPattern(
            "healthcare_facility",
            r"\b(?:hospital|clinic|medical center|physician).*?\b",
            RiskCategory.PHI, "high", "redact", 0.85,
            "Healthcare facility information detected"
        ),
        DetectionPattern(
            "health_record",
            r"[Hh]ealth\s+[Rr]ecord\s*:.*?(?:diagnosed|diagnosis).*?\d{4}-\d{2}-\d{2}",
            RiskCategory.PHI, "critical", "block", 0.95,
            "Health record with date detected"
        ),
        DetectionPattern(
            "phi_marker",
            r"\bPHI\s*:.*?(?:cholesterol|level|mg/dL)",
            RiskCategory.PHI, "critical", "block", 0.95,
            "PHI marker detected"
        ),
        DetectionPattern(
            "diagnosis_date",
            r"(?:diagnosed|diagnosis).*?(?:on|with).*?\d{4}-\d{2}-\d{2}",
            RiskCategory.PHI, "critical", "block", 0.9,
            "Diagnosis with date detected"
        ),
        DetectionPattern(
            "medical_card",
            r"\b(?:medical|patient).*?card.*?[Ii][Dd]\s*:?\s*(?:MC-)?[\dA-Z-]{6,}\b",
            RiskCategory.PHI, "critical", "block", 0.95,
            "Medical card ID detected"
        ),
        DetectionPattern(
            "disease_name_context",
            r"\b(?:patient|diagnosed|suffering).*?(?:HIV|AIDS|COVID).*?(?:suggest|treatment|advice)\b",
            RiskCategory.PHI, "critical", "block", 0.95,
            "Disease name in medical context detected"
        ),
    ]

    # PCI (Payment Card Industry) Patterns
    PCI_PATTERNS = [
        DetectionPattern(
            "credit_card",
            r"\b(?:\d{4}[-\s]?){3}\d{4}\b",
            RiskCategory.PCI, "critical", "block", 0.95,
            "Credit card number detected"
        ),
        DetectionPattern(
            "bank_account",
            r"\b[Bb]ank\s+[Aa]ccount\s*:?\s*\d{6,}\b",
            RiskCategory.PCI, "critical", "block", 0.95,
            "Bank account detected"
        ),
        DetectionPattern(
            "routing_number",
            r"\b[Rr]outing\s*:?\s*(?:0[2-6]\d{6}|0[89]\d{6}|[1-9]\d{8})\b",
            RiskCategory.PCI, "critical", "block", 0.95,
            "Bank routing number detected"
        ),
        DetectionPattern(
            "cvv",
            r"\b(?:cvv|cvc|security code).*?\d{3,4}\b",
            RiskCategory.PCI, "critical", "block", 0.95,
            "CVV/CVC security code detected"
        ),
        DetectionPattern(
            "financial_transaction",
            r"\b(?:transfer|withdraw|deposit).*?\$\d+[,\d]*\.?\d*\b",
            RiskCategory.PCI, "high", "redact", 0.9,
            "Financial transaction information detected"
        ),
        DetectionPattern(
            "bank_account_with_routing",
            r"\b[Bb]ank\s+[Aa]ccount\s*:?\s*\d{6,}\s*,\s*[Rr]outing\s+\d{9}\b",
            RiskCategory.PCI, "critical", "block", 0.95,
            "Bank account with routing detected"
        ),
    ]

    @classmethod
    def get_all_patterns(cls) -> List[DetectionPattern]:
        """Get all detection patterns"""
        return (
            cls.PROMPT_INJECTION_PATTERNS +
            cls.PII_PATTERNS +
            cls.PHI_PATTERNS +
            cls.PCI_PATTERNS
        )

    @classmethod
    def get_patterns_by_category(cls, category: RiskCategory) -> List[DetectionPattern]:
        """Get patterns for a specific category"""
        category_map = {
            RiskCategory.PROMPT_INJECTION: cls.PROMPT_INJECTION_PATTERNS,
            RiskCategory.PII: cls.PII_PATTERNS,
            RiskCategory.PHI: cls.PHI_PATTERNS,
            RiskCategory.PCI: cls.PCI_PATTERNS,
        }
        return category_map.get(category, [])

    @classmethod
    def detect_all(cls, text: str) -> List[Dict[str, Any]]:
        """Detect all patterns in text"""
        all_risks = []
        for pattern in cls.get_all_patterns():
            matches = pattern.detect(text)
            all_risks.extend(matches)
        
        # Remove duplicates (same match at same position)
        unique_risks = []
        seen = set()
        for risk in all_risks:
            key = (risk['start'], risk['end'], risk['match'])
            if key not in seen:
                seen.add(key)
                unique_risks.append(risk)
        
        return unique_risks

    @classmethod
    def detect_by_category(cls, text: str, category: RiskCategory) -> List[Dict[str, Any]]:
        """Detect patterns for a specific category"""
        risks = []
        for pattern in cls.get_patterns_by_category(category):
            matches = pattern.detect(text)
            risks.extend(matches)
        return risks


def categorize_risk_type(risk_type: str) -> str:
    """Categorize a risk type into one of the 4 main categories"""
    upper_type = risk_type.upper()
    
    if "INJECTION" in upper_type:
        return RiskCategory.PROMPT_INJECTION.value
    elif "PHI" in upper_type or "MEDICAL" in upper_type or "HEALTH" in upper_type:
        return RiskCategory.PHI.value
    elif "CREDIT_CARD" in upper_type or "PAYMENT" in upper_type or "BANK" in upper_type:
        return RiskCategory.PCI.value
    else:
        return RiskCategory.PII.value
