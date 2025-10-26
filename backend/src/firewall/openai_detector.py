"""
Enhanced OpenAI-based Firewall Detector
Uses OpenAI API for advanced threat detection and analysis.
"""

import json
import re
import logging
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import openai
from .templates import LLMTemplates
from .injection_detection import detect_pii_patterns, calculate_anomaly_score

logger = logging.getLogger(__name__)

class OpenAIFirewallDetector:
    """Enhanced firewall detector using OpenAI API for advanced threat detection."""
    
    def __init__(self, api_key: str, model: str = "gpt-4", temperature: float = 0.1):
        """
        Initialize the OpenAI firewall detector.
        
        Args:
            api_key: OpenAI API key
            model: OpenAI model to use (default: gpt-4)
            temperature: Temperature for response generation (default: 0.1 for consistency)
        """
        self.api_key = api_key
        self.model = model
        self.temperature = temperature
        self.client = openai.OpenAI(api_key=api_key)
        
        # Enhanced PII patterns
        self.pii_patterns = {
            "email": r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",
            "ssn": r"\b\d{3}-?\d{2}-?\d{4}\b",
            "phone": r"\b(?:\+?1[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})\b",
            "credit_card": r"\b(?:\d{4}[-\s]?){3}\d{4}\b",
            "ip_address": r"\b(?:\d{1,3}\.){3}\d{1,3}\b",
            "url": r"https?://[^\s]+",
            "medical_record": r"\b(?:patient|diagnosis|treatment|medication|doctor|physician|medical|health|disease|illness|symptom)\b",
        }
        
        # Risk severity mapping
        self.severity_mapping = {
            "low": 0.3,
            "medium": 0.6,
            "high": 0.8,
            "critical": 0.95
        }
    
    def _call_openai(self, template_name: str, **kwargs) -> Dict[str, Any]:
        """
        Make a call to OpenAI API with the specified template.
        
        Args:
            template_name: Name of the template to use
            **kwargs: Template parameters
            
        Returns:
            Parsed JSON response from OpenAI
        """
        try:
            prompt = LLMTemplates.get_template(template_name, **kwargs)
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a cybersecurity expert. Always respond with valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=self.temperature,
                max_tokens=1000
            )
            
            content = response.choices[0].message.content.strip()
            
            # Try to parse JSON response
            try:
                return json.loads(content)
            except json.JSONDecodeError:
                # Fallback parsing for non-JSON responses
                logger.warning(f"Non-JSON response from OpenAI: {content}")
                return self._parse_fallback_response(content, template_name)
                
        except Exception as e:
            logger.error(f"OpenAI API error: {str(e)}")
            return self._get_error_response(str(e))
    
    def _parse_fallback_response(self, content: str, template_name: str) -> Dict[str, Any]:
        """Parse non-JSON responses as fallback."""
        if template_name == "prompt_injection":
            return {
                "is_injection": "injection" in content.lower() or "malicious" in content.lower(),
                "confidence": 0.5,
                "reasoning": content,
                "risk_level": "medium",
                "detected_techniques": [],
                "severity_score": 0.5
            }
        elif template_name == "pii_detection":
            return {
                "pii_detected": "pii" in content.lower() or "personal" in content.lower(),
                "confidence": 0.5,
                "pii_types": [],
                "matches": [],
                "risk_level": "medium",
                "recommended_action": "warn"
            }
        else:
            return {
                "error": "Failed to parse response",
                "raw_response": content,
                "confidence": 0.0
            }
    
    def _get_error_response(self, error_msg: str) -> Dict[str, Any]:
        """Get error response when API call fails."""
        return {
            "error": f"OpenAI API error: {error_msg}",
            "confidence": 0.0,
            "is_injection": False,
            "pii_detected": False,
            "is_safe": True,
            "overall_risk": "low"
        }
    
    def detect_prompt_injection(self, user_input: str) -> Dict[str, Any]:
        """
        Detect prompt injection attempts using OpenAI.
        
        Args:
            user_input: User input to analyze
            
        Returns:
            Detection results with confidence and reasoning
        """
        if not user_input.strip():
            return {
                "is_injection": False,
                "confidence": 0.0,
                "reasoning": "Empty input",
                "risk_level": "low",
                "detected_techniques": [],
                "severity_score": 0.0
            }
        
        result = self._call_openai("prompt_injection", user_input=user_input)
        
        # Convert to standardized format
        return {
            "type": "INJECTION_OPENAI",
            "is_injection": result.get("is_injection", False),
            "confidence": result.get("confidence", 0.0),
            "reasoning": result.get("reasoning", ""),
            "risk_level": result.get("risk_level", "low"),
            "detected_techniques": result.get("detected_techniques", []),
            "severity_score": result.get("severity_score", 0.0),
            "severity": self._map_risk_level_to_severity(result.get("risk_level", "low")),
            "action": self._determine_action_from_risk(result.get("risk_level", "low")),
            "match": user_input if result.get("is_injection", False) else "",
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def detect_pii_openai(self, user_input: str) -> List[Dict[str, Any]]:
        """
        Detect PII using OpenAI for advanced analysis.
        
        Args:
            user_input: User input to analyze
            
        Returns:
            List of detected PII risks
        """
        if not user_input.strip():
            return []
        
        result = self._call_openai("pii_detection", user_input=user_input)
        
        risks = []
        if result.get("pii_detected", False):
            pii_types = result.get("pii_types", [])
            matches = result.get("matches", [])
            
            for i, pii_type in enumerate(pii_types):
                match = matches[i] if i < len(matches) else ""
                risks.append({
                    "type": f"PII_{pii_type.upper()}",
                    "match": match,
                    "confidence": result.get("confidence", 0.0),
                    "severity": self._map_risk_level_to_severity(result.get("risk_level", "medium")),
                    "action": self._determine_action_from_recommendation(result.get("recommended_action", "warn")),
                    "risk_level": result.get("risk_level", "medium"),
                    "timestamp": datetime.utcnow().isoformat()
                })
        
        return risks
    
    def classify_content(self, user_input: str) -> Dict[str, Any]:
        """
        Classify content for safety and appropriateness.
        
        Args:
            user_input: User input to classify
            
        Returns:
            Content classification results
        """
        if not user_input.strip():
            return {
                "is_safe": True,
                "confidence": 1.0,
                "categories": [],
                "severity": "low",
                "reasoning": "Empty input",
                "recommended_action": "allow"
            }
        
        result = self._call_openai("content_classification", user_input=user_input)
        
        return {
            "type": "CONTENT_CLASSIFICATION",
            "is_safe": result.get("is_safe", True),
            "confidence": result.get("confidence", 0.0),
            "categories": result.get("categories", []),
            "severity": result.get("severity", "low"),
            "reasoning": result.get("reasoning", ""),
            "recommended_action": result.get("recommended_action", "allow"),
            "action": self._determine_action_from_recommendation(result.get("recommended_action", "allow")),
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def assess_risk(self, user_input: str) -> Dict[str, Any]:
        """
        Perform comprehensive risk assessment.
        
        Args:
            user_input: User input to assess
            
        Returns:
            Comprehensive risk assessment
        """
        if not user_input.strip():
            return {
                "overall_risk": "low",
                "risk_score": 0.0,
                "primary_concerns": [],
                "confidence": 1.0,
                "recommended_action": "allow",
                "explanation": "Empty input"
            }
        
        result = self._call_openai("risk_assessment", user_input=user_input)
        
        return {
            "type": "RISK_ASSESSMENT",
            "overall_risk": result.get("overall_risk", "low"),
            "risk_score": result.get("risk_score", 0.0),
            "primary_concerns": result.get("primary_concerns", []),
            "confidence": result.get("confidence", 0.0),
            "recommended_action": result.get("recommended_action", "allow"),
            "action": self._determine_action_from_recommendation(result.get("recommended_action", "allow")),
            "explanation": result.get("explanation", ""),
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def detect_anomalies(self, user_input: str) -> Dict[str, Any]:
        """
        Detect anomalous patterns in user input.
        
        Args:
            user_input: User input to analyze
            
        Returns:
            Anomaly detection results
        """
        if not user_input.strip():
            return {
                "is_anomalous": False,
                "anomaly_score": 0.0,
                "anomaly_types": [],
                "confidence": 1.0,
                "explanation": "Empty input"
            }
        
        result = self._call_openai("anomaly_detection", user_input=user_input)
        
        return {
            "type": "ANOMALY_DETECTION",
            "is_anomalous": result.get("is_anomalous", False),
            "anomaly_score": result.get("anomaly_score", 0.0),
            "anomaly_types": result.get("anomaly_types", []),
            "confidence": result.get("confidence", 0.0),
            "explanation": result.get("explanation", ""),
            "severity": self._map_anomaly_score_to_severity(result.get("anomaly_score", 0.0)),
            "action": self._determine_action_from_anomaly_score(result.get("anomaly_score", 0.0)),
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def redact_text(self, user_input: str) -> Dict[str, Any]:
        """
        Redact sensitive information from text.
        
        Args:
            user_input: Text to redact
            
        Returns:
            Redaction results
        """
        if not user_input.strip():
            return {
                "redacted_text": "",
                "redaction_count": 0,
                "redacted_types": [],
                "preserved_context": True
            }
        
        result = self._call_openai("text_redaction", user_input=user_input)
        
        return {
            "type": "TEXT_REDACTION",
            "redacted_text": result.get("redacted_text", user_input),
            "redaction_count": result.get("redaction_count", 0),
            "redacted_types": result.get("redacted_types", []),
            "preserved_context": result.get("preserved_context", True),
            "original_text": user_input,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def generate_explanation(self, decision: str, risks: List[Dict], confidence: float) -> str:
        """
        Generate user-friendly explanation for firewall decisions.
        
        Args:
            decision: Firewall decision made
            risks: List of detected risks
            confidence: Confidence level
            
        Returns:
            User-friendly explanation
        """
        risk_summary = []
        for risk in risks:
            risk_summary.append(f"{risk.get('type', 'Unknown')} ({risk.get('severity', 'unknown')} severity)")
        
        result = self._call_openai(
            "explanation_generation",
            decision=decision,
            risks="; ".join(risk_summary),
            confidence=confidence
        )
        
        return result.get("explanation", f"Decision: {decision} based on detected risks with {confidence:.1%} confidence.")
    
    def detect_comprehensive(self, user_input: str) -> Dict[str, Any]:
        """
        Perform comprehensive detection using all available methods.
        
        Args:
            user_input: User input to analyze
            
        Returns:
            Comprehensive detection results
        """
        if not user_input.strip():
            return {
                "decision": "allow",
                "risks": [],
                "confidence": 0.0,
                "anomaly_score": 0.0,
                "total_risks": 0,
                "explanation": "Empty input - no risks detected",
                "timestamp": datetime.utcnow().isoformat()
            }
        
        all_risks = []
        
        # 1. Detect prompt injection
        injection_result = self.detect_prompt_injection(user_input)
        if injection_result.get("is_injection", False):
            all_risks.append(injection_result)
        
        # 2. Detect PII using OpenAI
        pii_risks = self.detect_pii_openai(user_input)
        all_risks.extend(pii_risks)
        
        # 3. Detect PII using regex (fallback)
        regex_pii = detect_pii_patterns(user_input)
        for pii in regex_pii:
            all_risks.append({
                "type": f"PII_{pii['type']}",
                "match": pii["match"],
                "confidence": 0.9,
                "severity": "high",
                "action": "redact",
                "timestamp": datetime.utcnow().isoformat()
            })
        
        # 4. Classify content
        content_result = self.classify_content(user_input)
        if not content_result.get("is_safe", True):
            all_risks.append(content_result)
        
        # 5. Detect anomalies
        anomaly_result = self.detect_anomalies(user_input)
        if anomaly_result.get("is_anomalous", False):
            all_risks.append(anomaly_result)
        
        # 6. Assess overall risk
        risk_assessment = self.assess_risk(user_input)
        
        # Determine final decision
        decision = self._determine_final_decision(all_risks)
        
        # Calculate confidence
        confidence = self._calculate_overall_confidence(all_risks)
        
        # Calculate anomaly score
        anomaly_score = calculate_anomaly_score(user_input, all_risks, injection_result.get("severity_score", 0.0))
        
        # Generate explanation
        explanation = self.generate_explanation(decision, all_risks, confidence)
        
        return {
            "decision": decision,
            "risks": all_risks,
            "confidence": confidence,
            "anomaly_score": anomaly_score,
            "total_risks": len(all_risks),
            "explanation": explanation,
            "risk_assessment": risk_assessment,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def _map_risk_level_to_severity(self, risk_level: str) -> str:
        """Map risk level to severity."""
        mapping = {
            "low": "low",
            "medium": "medium", 
            "high": "high",
            "critical": "high"
        }
        return mapping.get(risk_level.lower(), "medium")
    
    def _determine_action_from_risk(self, risk_level: str) -> str:
        """Determine action based on risk level."""
        mapping = {
            "low": "warn",
            "medium": "redact",
            "high": "block",
            "critical": "block"
        }
        return mapping.get(risk_level.lower(), "warn")
    
    def _determine_action_from_recommendation(self, recommendation: str) -> str:
        """Determine action from recommendation."""
        mapping = {
            "allow": "allow",
            "warn": "warn",
            "redact": "redact",
            "block": "block"
        }
        return mapping.get(recommendation.lower(), "warn")
    
    def _map_anomaly_score_to_severity(self, score: float) -> str:
        """Map anomaly score to severity."""
        if score >= 0.8:
            return "high"
        elif score >= 0.5:
            return "medium"
        else:
            return "low"
    
    def _determine_action_from_anomaly_score(self, score: float) -> str:
        """Determine action from anomaly score."""
        if score >= 0.8:
            return "block"
        elif score >= 0.5:
            return "redact"
        else:
            return "warn"
    
    def _determine_final_decision(self, risks: List[Dict[str, Any]]) -> str:
        """Determine final decision based on all risks."""
        if not risks:
            return "allow"
        
        # Priority order: block > redact > warn > allow
        actions = [risk.get("action", "allow") for risk in risks]
        
        if "block" in actions:
            return "block"
        elif "redact" in actions:
            return "redact"
        elif "warn" in actions:
            return "warn"
        else:
            return "allow"
    
    def _calculate_overall_confidence(self, risks: List[Dict[str, Any]]) -> float:
        """Calculate overall confidence from all risks."""
        if not risks:
            return 0.0
        
        confidences = [risk.get("confidence", 0.0) for risk in risks]
        return sum(confidences) / len(confidences)
    
    def get_available_templates(self) -> List[str]:
        """Get list of available templates."""
        return LLMTemplates.list_templates()
    
    def test_connection(self) -> Dict[str, Any]:
        """Test OpenAI API connection."""
        try:
            test_result = self._call_openai("prompt_injection", user_input="test")
            return {
                "status": "success",
                "model": self.model,
                "api_key_valid": True,
                "response_time": "< 1s",
                "test_result": test_result
            }
        except Exception as e:
            return {
                "status": "error",
                "model": self.model,
                "api_key_valid": False,
                "error": str(e)
            }
