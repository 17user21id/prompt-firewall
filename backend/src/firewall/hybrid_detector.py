"""
Hybrid Firewall Detector
Combines traditional regex-based detection with OpenAI-powered analysis.
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from .detector import FirewallDetector
from .openai_detector import OpenAIFirewallDetector
from .templates import LLMTemplates

logger = logging.getLogger(__name__)

class HybridFirewallDetector:
    """
    Hybrid firewall detector that combines:
    1. Fast regex-based detection for immediate threats
    2. OpenAI-powered analysis for complex scenarios
    3. Fallback mechanisms for reliability
    """
    
    def __init__(self, openai_api_key: Optional[str] = None, openai_model: str = "gpt-4"):
        """
        Initialize the hybrid detector.
        
        Args:
            openai_api_key: OpenAI API key (optional)
            openai_model: OpenAI model to use
        """
        # Initialize traditional detector
        self.traditional_detector = FirewallDetector(
            openai_api_key=openai_api_key,
            openai_model=openai_model
        )
        
        # Initialize OpenAI detector if API key provided
        self.openai_detector = None
        if openai_api_key:
            try:
                self.openai_detector = OpenAIFirewallDetector(
                    api_key=openai_api_key,
                    model=openai_model
                )
                logger.info("OpenAI detector initialized successfully")
            except Exception as e:
                logger.warning(f"Failed to initialize OpenAI detector: {e}")
                self.openai_detector = None
        
        # Detection modes
        self.modes = {
            "fast": "Traditional regex-based detection only",
            "balanced": "Traditional + OpenAI for complex cases",
            "comprehensive": "Full OpenAI analysis for all inputs"
        }
        self.current_mode = "balanced"
        
        # Performance metrics
        self.metrics = {
            "total_requests": 0,
            "traditional_detections": 0,
            "openai_detections": 0,
            "fallback_detections": 0,
            "average_response_time": 0.0
        }
    
    def detect(self, user_input: str, mode: Optional[str] = None) -> Dict[str, Any]:
        """
        Perform detection using the specified mode.
        
        Args:
            user_input: User input to analyze
            mode: Detection mode ("fast", "balanced", "comprehensive")
            
        Returns:
            Detection results
        """
        start_time = datetime.utcnow()
        self.metrics["total_requests"] += 1
        
        detection_mode = mode or self.current_mode
        
        try:
            if detection_mode == "fast":
                result = self._fast_detection(user_input)
            elif detection_mode == "balanced":
                result = self._balanced_detection(user_input)
            elif detection_mode == "comprehensive":
                result = self._comprehensive_detection(user_input)
            else:
                logger.warning(f"Unknown mode '{detection_mode}', falling back to balanced")
                result = self._balanced_detection(user_input)
            
            # Update metrics
            end_time = datetime.utcnow()
            response_time = (end_time - start_time).total_seconds()
            self._update_metrics(response_time, detection_mode)
            
            return result
            
        except Exception as e:
            logger.error(f"Detection error: {e}")
            return self._fallback_detection(user_input)
    
    def _fast_detection(self, user_input: str) -> Dict[str, Any]:
        """Fast detection using only traditional methods."""
        self.metrics["traditional_detections"] += 1
        return self.traditional_detector.detect(user_input)
    
    def _balanced_detection(self, user_input: str) -> Dict[str, Any]:
        """
        Balanced detection: traditional first, OpenAI for complex cases.
        """
        # Start with traditional detection
        traditional_result = self.traditional_detector.detect(user_input)
        
        # If traditional detection finds high-risk items, use OpenAI for confirmation
        high_risk_found = any(
            risk.get("severity") == "high" or risk.get("action") == "block"
            for risk in traditional_result.get("risks", [])
        )
        
        # If OpenAI is available and we have high-risk items, get additional analysis
        if self.openai_detector and (high_risk_found or len(user_input) > 100):
            try:
                openai_result = self.openai_detector.detect_comprehensive(user_input)
                self.metrics["openai_detections"] += 1
                
                # Merge results, prioritizing OpenAI for high-risk items
                return self._merge_results(traditional_result, openai_result)
            except Exception as e:
                logger.warning(f"OpenAI detection failed: {e}")
                self.metrics["fallback_detections"] += 1
        
        self.metrics["traditional_detections"] += 1
        return traditional_result
    
    def _comprehensive_detection(self, user_input: str) -> Dict[str, Any]:
        """Comprehensive detection using OpenAI for all inputs."""
        if self.openai_detector:
            try:
                result = self.openai_detector.detect_comprehensive(user_input)
                self.metrics["openai_detections"] += 1
                return result
            except Exception as e:
                logger.warning(f"OpenAI detection failed: {e}")
                self.metrics["fallback_detections"] += 1
        
        # Fallback to traditional detection
        return self._fast_detection(user_input)
    
    def _fallback_detection(self, user_input: str) -> Dict[str, Any]:
        """Fallback detection when all else fails."""
        self.metrics["fallback_detections"] += 1
        logger.warning("Using fallback detection")
        
        return {
            "decision": "warn",
            "risks": [{
                "type": "SYSTEM_ERROR",
                "match": user_input[:50] + "..." if len(user_input) > 50 else user_input,
                "confidence": 0.5,
                "severity": "medium",
                "action": "warn",
                "reasoning": "System error occurred during detection"
            }],
            "confidence": 0.5,
            "anomaly_score": 0.5,
            "total_risks": 1,
            "explanation": "Detection system encountered an error. Proceeding with caution.",
            "timestamp": datetime.utcnow().isoformat(),
            "fallback": True
        }
    
    def _merge_results(self, traditional: Dict[str, Any], openai: Dict[str, Any]) -> Dict[str, Any]:
        """
        Merge traditional and OpenAI detection results.
        
        Args:
            traditional: Results from traditional detector
            openai: Results from OpenAI detector
            
        Returns:
            Merged results
        """
        # Combine risks, avoiding duplicates
        all_risks = traditional.get("risks", [])
        openai_risks = openai.get("risks", [])
        
        # Add OpenAI risks that don't duplicate traditional ones
        for openai_risk in openai_risks:
            if not self._risk_exists(all_risks, openai_risk):
                all_risks.append(openai_risk)
        
        # Determine final decision (prioritize more restrictive actions)
        decision = self._determine_final_decision(all_risks)
        
        # Calculate combined confidence
        traditional_conf = traditional.get("confidence", 0.0)
        openai_conf = openai.get("confidence", 0.0)
        combined_confidence = (traditional_conf + openai_conf) / 2
        
        # Use OpenAI explanation if available, otherwise traditional
        explanation = openai.get("explanation") or traditional.get("explanation", "No explanation available")
        
        return {
            "decision": decision,
            "risks": all_risks,
            "confidence": combined_confidence,
            "anomaly_score": max(traditional.get("anomaly_score", 0.0), openai.get("anomaly_score", 0.0)),
            "total_risks": len(all_risks),
            "explanation": explanation,
            "timestamp": datetime.utcnow().isoformat(),
            "detection_method": "hybrid",
            "traditional_confidence": traditional_conf,
            "openai_confidence": openai_conf
        }
    
    def _risk_exists(self, existing_risks: List[Dict], new_risk: Dict) -> bool:
        """Check if a risk already exists in the list."""
        for existing in existing_risks:
            if (existing.get("type") == new_risk.get("type") and 
                existing.get("match") == new_risk.get("match")):
                return True
        return False
    
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
    
    def _update_metrics(self, response_time: float, mode: str):
        """Update performance metrics."""
        # Update average response time
        total_requests = self.metrics["total_requests"]
        current_avg = self.metrics["average_response_time"]
        self.metrics["average_response_time"] = (
            (current_avg * (total_requests - 1) + response_time) / total_requests
        )
    
    def set_mode(self, mode: str):
        """Set the detection mode."""
        if mode in self.modes:
            self.current_mode = mode
            logger.info(f"Detection mode set to: {mode}")
        else:
            logger.warning(f"Invalid mode '{mode}'. Available modes: {list(self.modes.keys())}")
    
    def get_mode(self) -> str:
        """Get current detection mode."""
        return self.current_mode
    
    def get_available_modes(self) -> Dict[str, str]:
        """Get available detection modes."""
        return self.modes.copy()
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get performance metrics."""
        return self.metrics.copy()
    
    def reset_metrics(self):
        """Reset performance metrics."""
        self.metrics = {
            "total_requests": 0,
            "traditional_detections": 0,
            "openai_detections": 0,
            "fallback_detections": 0,
            "average_response_time": 0.0
        }
    
    def test_openai_connection(self) -> Dict[str, Any]:
        """Test OpenAI API connection."""
        if self.openai_detector:
            return self.openai_detector.test_connection()
        else:
            return {
                "status": "error",
                "message": "OpenAI detector not initialized",
                "api_key_provided": False
            }
    
    def get_available_templates(self) -> List[str]:
        """Get available LLM templates."""
        return LLMTemplates.list_templates()
    
    def detect_prompt_injection(self, user_input: str) -> Dict[str, Any]:
        """Detect prompt injection using the best available method."""
        if self.openai_detector:
            return self.openai_detector.detect_prompt_injection(user_input)
        else:
            return self.traditional_detector.detect_injection_heuristic(user_input)
    
    def detect_pii(self, user_input: str) -> List[Dict[str, Any]]:
        """Detect PII using the best available method."""
        if self.openai_detector:
            return self.openai_detector.detect_pii_openai(user_input)
        else:
            return self.traditional_detector.detect_pii(user_input)
    
    def redact_text(self, user_input: str) -> str:
        """Redact sensitive information from text."""
        if self.openai_detector:
            result = self.openai_detector.redact_text(user_input)
            return result.get("redacted_text", user_input)
        else:
            risks = self.traditional_detector.detect_pii(user_input)
            return self.traditional_detector.redact_text(user_input, risks)
    
    def generate_explanation(self, decision: str, risks: List[Dict], confidence: float) -> str:
        """Generate explanation for firewall decisions."""
        if self.openai_detector:
            return self.openai_detector.generate_explanation(decision, risks, confidence)
        else:
            return self.traditional_detector.get_explanation(risks)
