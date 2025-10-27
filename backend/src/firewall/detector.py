"""
FirewallDetector - Core detection engine for PII, PHI, PCI, and prompt injection.
Combines multiple detection methods for comprehensive security analysis.
"""

import re
from typing import List, Dict, Any
from .injection_detection import (
    detect_prompt_injection_using_heuristic_on_input,
    detect_pii_patterns,
    calculate_anomaly_score,
    call_openai_to_detect_pi,
    render_prompt_for_pi_detection
)
from .detection_patterns import (
    DetectionPatternRegistry,
    RiskCategory,
    categorize_risk_type
)
from ..common.firewall_constants import (
    FirewallConstants,
    SeverityLevel,
    ActionType
)
from ..common.regex_constants import RegexConstants

class FirewallDetector:
    """Detects PII and prompt injections in user input."""
    
    def __init__(self, openai_api_key: str = None, openai_model: str = "gpt-4"):
        self.openai_api_key = openai_api_key
        self.openai_model = openai_model
        
        # Enhanced PII patterns
        self.pii_patterns = {
            "email": {
                "pattern": RegexConstants.EMAIL_PATTERN,
                "severity": SeverityLevel.HIGH.value,
                "action": ActionType.REDACT.value
            },
            "ssn": {
                "pattern": RegexConstants.SSN_PATTERN_VARIANT,
                "severity": SeverityLevel.HIGH.value,
                "action": ActionType.BLOCK.value
            },
            "phone": {
                "pattern": RegexConstants.PHONE_PATTERN_ENHANCED,
                "severity": SeverityLevel.MEDIUM.value,
                "action": ActionType.REDACT.value
            },
            "credit_card": {
                "pattern": RegexConstants.CREDIT_CARD_PATTERN_VARIANT,
                "severity": SeverityLevel.HIGH.value,
                "action": ActionType.BLOCK.value
            },
            "ip_address": {
                "pattern": RegexConstants.IP_ADDRESS_PATTERN_ENHANCED,
                "severity": SeverityLevel.MEDIUM.value,
                "action": ActionType.WARN.value
            },
            "url": {
                "pattern": RegexConstants.URL_PATTERN,
                "severity": SeverityLevel.LOW.value,
                "action": ActionType.WARN.value
            },
            "medical_record": {
                "pattern": RegexConstants.MEDICAL_RECORD_GENERAL_PATTERN,
                "severity": SeverityLevel.HIGH.value,
                "action": ActionType.BLOCK.value
            }
        }

    def detect_pii(self, prompt: str) -> List[Dict]:
        """Detect PII in the prompt using enhanced patterns."""
        risks = []
        
        for pii_type, config in self.pii_patterns.items():
            pattern = config["pattern"]
            severity = config["severity"]
            action = config["action"]
            
            matches = re.finditer(pattern, prompt, re.IGNORECASE)
            for match in matches:
                risks.append({
                    "type": f"PII_{pii_type.upper()}",
                    "match": match.group(),
                    "start": match.start(),
                    "end": match.end(),
                    "severity": severity,
                    "action": action,
                    "confidence": FirewallConstants.DEFAULT_CONFIDENCE_REGEX
                })
        
        return risks

    def detect_injection_heuristic(self, prompt: str) -> List[Dict]:
        """Detect prompt injections using heuristic method."""
        score = detect_prompt_injection_using_heuristic_on_input(prompt)
        
        # Use constants for thresholds
        if score > FirewallConstants.INJECTION_DETECTION_THRESHOLD:
            if score > FirewallConstants.INJECTION_SEVERE_THRESHOLD:
                severity = SeverityLevel.HIGH.value
                action = ActionType.BLOCK.value
            elif score > FirewallConstants.INJECTION_MEDIUM_THRESHOLD:
                severity = SeverityLevel.MEDIUM.value
                action = ActionType.WARN.value
            else:
                severity = SeverityLevel.LOW.value
                action = ActionType.WARN.value
            
            return [{
                "type": FirewallConstants.RISK_TYPE_INJECTION,
                "match": prompt[:100] + "..." if len(prompt) > 100 else prompt,
                "severity": severity,
                "action": action,
                "confidence": score,
                "score": score
            }]
        
        return []

    def detect_injection_openai(self, prompt: str) -> List[Dict]:
        """Detect prompt injections using OpenAI (if API key provided)."""
        if not self.openai_api_key:
            return []
        
        try:
            rendered_prompt = render_prompt_for_pi_detection(prompt)
            response = call_openai_to_detect_pi(rendered_prompt, self.openai_model, self.openai_api_key)
            
            if response.get("is_injection", False):
                confidence = response.get("confidence", 0.5)
                risk_level = response.get("risk_level", "medium")
                
                severity = "high" if risk_level == "high" else "medium" if risk_level == "medium" else "low"
                action = "block" if risk_level == "high" else "warn"
                
                return [{
                    "type": "INJECTION_OPENAI",
                    "match": prompt[:100] + "..." if len(prompt) > 100 else prompt,
                    "severity": severity,
                    "action": action,
                    "confidence": confidence,
                    "reasoning": response.get("reasoning", ""),
                    "score": confidence
                }]
        
        except Exception as e:
            print(f"OpenAI detection error: {e}")
        
        return []

    def detect_custom_patterns(self, prompt: str, custom_rules: List[Dict]) -> List[Dict]:
        """Detect patterns using custom rules."""
        risks = []
        
        for rule in custom_rules:
            pattern = rule.get("pattern", "")
            rule_type = rule.get("type", "CUSTOM")
            severity = rule.get("severity", "medium")
            action = rule.get("action", "warn")
            
            # Map common rule types to valid RiskType enum values
            type_mapping = {
                "PII": "CUSTOM",
                "EMAIL": "PII_EMAIL",
                "SSN": "PII_SSN",
                "PHONE": "PII_PHONE",
                "CREDIT_CARD": "PII_CREDIT_CARD",
                "IP_ADDRESS": "PII_IP_ADDRESS",
                "URL": "PII_URL",
                "MEDICAL_RECORD": "PII_MEDICAL_RECORD",
                "INJECTION": "INJECTION"
            }
            
            mapped_type = type_mapping.get(rule_type.upper(), rule_type.upper())
            # Ensure it's a valid type, otherwise use CUSTOM
            valid_types = ["PII_EMAIL", "PII_SSN", "PII_PHONE", "PII_CREDIT_CARD", "PII_IP_ADDRESS", 
                          "PII_URL", "PII_MEDICAL_RECORD", "INJECTION", "INJECTION_OPENAI", "CUSTOM"]
            if mapped_type not in valid_types:
                mapped_type = "CUSTOM"
            
            try:
                matches = re.finditer(pattern, prompt, re.IGNORECASE)
                for match in matches:
                    risks.append({
                        "type": mapped_type,
                        "match": match.group(),
                        "start": match.start(),
                        "end": match.end(),
                        "severity": severity,
                        "action": action,
                        "confidence": 0.8,
                        "rule_id": rule.get("rule_id", "")
                    })
            except re.error as e:
                print(f"Invalid regex pattern in rule: {pattern}, error: {e}")
        
        return risks

    def detect(self, prompt: str, custom_rules: List[Dict] = None, use_openai: bool = False) -> Dict[str, Any]:
        """Comprehensive detection combining all methods - supports PII, PHI, PCI, and Prompt Injection."""
        if not prompt or len(prompt.strip()) == 0:
            return {
                "risks": [],
                "anomaly_score": 0.0,
                "decision": "allow",
                "confidence": 0.0,
                "risk_categories": {}
            }
        
        all_risks = []
        
        # Use new modular detection patterns for all categories
        modular_risks = DetectionPatternRegistry.detect_all(prompt)
        all_risks.extend(modular_risks)
        
        # Detect prompt injection using heuristics/OpenAI
        injection_risks = self.detect_injection_openai(prompt) if use_openai else self.detect_injection_heuristic(prompt)
        all_risks.extend(injection_risks)
        
        # Detect custom patterns
        if custom_rules:
            custom_risks = self.detect_custom_patterns(prompt, custom_rules)
            all_risks.extend(custom_risks)
        
        # Calculate anomaly score
        anomaly_score = calculate_anomaly_score(prompt, all_risks, 
                                               injection_risks[0].get("score", 0.0) if injection_risks else 0.0)
        
        # Categorize risks by main category (PII, PHI, PCI, PROMPT_INJECTION)
        risk_categories = self._categorize_risks(all_risks)
        
        # Determine overall decision
        decision = self._determine_decision(all_risks)
        
        # Calculate overall confidence
        confidence = self._calculate_confidence(all_risks)
        
        # Calculate overall severity
        overall_severity = self._calculate_overall_severity(all_risks)
        
        # Get unique risk categories list
        detected_categories = self._get_detected_categories(all_risks)
        
        return {
            "risks": all_risks,
            "anomaly_score": anomaly_score,
            "decision": decision,
            "confidence": confidence,
            "total_risks": len(all_risks),
            "risk_categories": risk_categories,
            "detected_categories": detected_categories,
            "severity": overall_severity,
            "high_severity_risks": len([r for r in all_risks if r.get("severity") == "high"]),
            "medium_severity_risks": len([r for r in all_risks if r.get("severity") == "medium"]),
            "low_severity_risks": len([r for r in all_risks if r.get("severity") == "low"])
        }
    
    def _categorize_risks(self, risks: List[Dict]) -> Dict[str, Any]:
        """Categorize risks by main category"""
        categories = {
            RiskCategory.PROMPT_INJECTION.value: [],
            RiskCategory.PII.value: [],
            RiskCategory.PHI.value: [],
            RiskCategory.PCI.value: []
        }
        
        for risk in risks:
            risk_type = risk.get("type", "")
            category = categorize_risk_type(risk_type)
            if category in categories:
                categories[category].append(risk)
        
        # Return counts and details
        return {
            "PROMPT_INJECTION": {
                "count": len(categories[RiskCategory.PROMPT_INJECTION.value]),
                "risks": categories[RiskCategory.PROMPT_INJECTION.value]
            },
            "PII": {
                "count": len(categories[RiskCategory.PII.value]),
                "risks": categories[RiskCategory.PII.value]
            },
            "PHI": {
                "count": len(categories[RiskCategory.PHI.value]),
                "risks": categories[RiskCategory.PHI.value]
            },
            "PCI": {
                "count": len(categories[RiskCategory.PCI.value]),
                "risks": categories[RiskCategory.PCI.value]
            }
        }

    def _determine_decision(self, risks: List[Dict]) -> str:
        """Determine the overall decision based on detected risks."""
        if not risks:
            return ActionType.ALLOW.value
        
        # Check for blocking risks
        blocking_risks = [r for r in risks if r.get("action") == ActionType.BLOCK.value]
        if blocking_risks:
            return ActionType.BLOCK.value
        
        # Check for redaction risks
        redaction_risks = [r for r in risks if r.get("action") == ActionType.REDACT.value]
        if redaction_risks:
            return ActionType.REDACT.value
        
        # Check for warning risks
        warning_risks = [r for r in risks if r.get("action") == ActionType.WARN.value]
        if warning_risks:
            return ActionType.WARN.value
        
        return ActionType.ALLOW.value

    def _calculate_confidence(self, risks: List[Dict]) -> float:
        """Calculate overall confidence in the detection."""
        if not risks:
            return 0.0
        
        total_confidence = sum(r.get("confidence", 0.5) for r in risks)
        return min(total_confidence / len(risks), 1.0)
    
    def _calculate_overall_severity(self, risks: List[Dict]) -> str:
        """Calculate overall severity based on detected risks."""
        if not risks:
            return SeverityLevel.LOW.value
        
        # Get all severities
        severities = [r.get("severity", SeverityLevel.LOW.value) for r in risks]
        
        # Count severities
        severity_counts = {
            SeverityLevel.CRITICAL.value: 0, 
            SeverityLevel.HIGH.value: 0, 
            SeverityLevel.MEDIUM.value: 0, 
            SeverityLevel.LOW.value: 0
        }
        for severity in severities:
            if severity in severity_counts:
                severity_counts[severity] += 1
        
        # Determine overall severity - Critical takes precedence
        if severity_counts[SeverityLevel.CRITICAL.value] > 0:
            return SeverityLevel.CRITICAL.value
        elif severity_counts[SeverityLevel.HIGH.value] > 0:
            return SeverityLevel.HIGH.value
        elif severity_counts[SeverityLevel.MEDIUM.value] > 0:
            return SeverityLevel.MEDIUM.value
        else:
            return SeverityLevel.LOW.value
    
    def _get_detected_categories(self, risks: List[Dict]) -> List[str]:
        """Get list of unique risk categories detected."""
        categories = set()
        for risk in risks:
            category = risk.get("category")
            if category:
                categories.add(category)
        return sorted(list(categories))

    def redact_text(self, text: str, risks: List[Dict]) -> str:
        """Redact sensitive information from text."""
        if not risks:
            return text
        
        # Sort risks by position (end to start) to avoid index shifting
        redaction_risks = [r for r in risks if r.get("action") == ActionType.REDACT.value]
        redaction_risks.sort(key=lambda x: x.get("end", 0), reverse=True)
        
        redacted_text = text
        
        for risk in redaction_risks:
            start = risk.get("start", 0)
            end = risk.get("end", 0)
            match = risk.get("match", "")
            
            if start < end and match:
                redacted_text = redacted_text[:start] + FirewallConstants.REDACTED_TEXT + redacted_text[end:]
        
        return redacted_text

    def get_explanation(self, risks: List[Dict]) -> str:
        """Generate human-readable explanation for detected risks."""
        if not risks:
            return "No security risks detected."
        
        explanations = []
        
        for risk in risks:
            risk_type = risk.get("type", "Unknown")
            severity = risk.get("severity", "unknown")
            match = risk.get("match", "")
            
            if "PII" in risk_type:
                explanations.append(f"Detected {risk_type} ({severity} severity): {match}")
            elif "INJECTION" in risk_type:
                explanations.append(f"Detected prompt injection attempt ({severity} severity)")
            else:
                explanations.append(f"Detected {risk_type} pattern ({severity} severity): {match}")
        
        return "; ".join(explanations)

    def validate_pattern(self, pattern: str) -> bool:
        """Validate if a regex pattern is valid."""
        try:
            re.compile(pattern)
            return True
        except re.error:
            return False
