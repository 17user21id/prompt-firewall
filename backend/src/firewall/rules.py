"""
FirewallRules - Rule application engine for processing detected risks.
Applies tenant-specific rules and policies to determine final actions.
"""

from typing import Dict, List, Any
from datetime import datetime, timezone
import re

from ..common.firewall_constants import (
    FirewallConstants, 
    SeverityLevel, 
    ActionType,
    RiskCategoryType,
)

class FirewallRules:
    """Applies rules to determine firewall actions."""
    
    def __init__(self):
        from ..common.firewall_constants import ActionType
        self.default_actions = {
            ActionType.BLOCK.value: [ActionType.BLOCK.value, "deny", "reject"],
            ActionType.REDACT.value: [ActionType.REDACT.value, "mask", "hide", "remove"],
            ActionType.WARN.value: [ActionType.WARN.value, "alert", "notify"],
            ActionType.ALLOW.value: [ActionType.ALLOW.value, "permit", "pass"]
        }

    def apply(self, prompt: str, risks: List[Dict], rules: List[Dict]) -> Dict:
        """Apply tenant-specific rules to the prompt and detected risks."""
        if not risks:
            return {
                "action": ActionType.ALLOW.value,
                "modified": prompt,
                "risks": [],
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "reason": "No risks detected",
                "applied_rules": []
            }
        
        # Sort rules by priority (severity and version)
        sorted_rules = self._sort_rules_by_priority(rules)
        
        # Apply rules to determine final action
        final_action = ActionType.ALLOW.value
        modified_prompt = prompt
        applied_rules = []
        reason_parts = []
        
        for risk in risks:
            risk_type = risk.get("type", "")
            risk_severity = risk.get("severity", SeverityLevel.LOW.value)
            risk_action = risk.get("action", ActionType.WARN.value)
            
            # Find applicable rules for this risk
            applicable_rules = self._find_applicable_rules(risk, sorted_rules)
            
            if applicable_rules:
                # Use the highest priority rule
                rule = applicable_rules[0]
                rule_action = rule.get("action", risk_action)
                rule_severity = rule.get("severity", risk_severity)
                
                # Update final action based on rule
                final_action = self._update_action(final_action, rule_action)
                
                # Apply rule-specific modifications
                if rule_action == ActionType.REDACT.value:
                    modified_prompt = self._apply_redaction(modified_prompt, risk)
                    reason_parts.append(f"Redacted {risk_type}: {risk.get('match', '')}")
                elif rule_action == ActionType.BLOCK.value:
                    modified_prompt = ""
                    reason_parts.append(f"Blocked {risk_type}: {risk.get('match', '')}")
                elif rule_action == ActionType.WARN.value:
                    reason_parts.append(f"Warning for {risk_type}: {risk.get('match', '')}")
                
                applied_rules.append({
                    "rule_id": rule.get("rule_id", ""),
                    "type": rule.get("type", ""),
                    "action": rule_action,
                    "severity": rule_severity,
                    "pattern": rule.get("pattern", ""),
                    "description": rule.get("description", "")
                })
            else:
                # Use default risk action
                final_action = self._update_action(final_action, risk_action)
                
                if risk_action == ActionType.REDACT.value:
                    modified_prompt = self._apply_redaction(modified_prompt, risk)
                    reason_parts.append(f"Redacted {risk_type}: {risk.get('match', '')}")
                elif risk_action == ActionType.BLOCK.value:
                    modified_prompt = ""
                    reason_parts.append(f"Blocked {risk_type}: {risk.get('match', '')}")
                elif risk_action == ActionType.WARN.value:
                    reason_parts.append(f"Warning for {risk_type}: {risk.get('match', '')}")
        
        # Generate final reason - structured format
        reason = self._generate_structured_reason(final_action, risks)

        # Deduplicate applied rules (unique by rule_id if present, else by type+pattern)
        unique_applied = []
        seen = set()
        for ar in applied_rules:
            key = ar.get("rule_id") or (ar.get("type"), ar.get("pattern"))
            if key in seen:
                continue
            seen.add(key)
            unique_applied.append(ar)
        
        return {
            "action": final_action,
            "modified": modified_prompt,
            "risks": risks,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "reason": reason,
            "applied_rules": unique_applied,
            "total_rules_applied": len(unique_applied)
        }

    def _sort_rules_by_priority(self, rules: List[Dict]) -> List[Dict]:
        """Sort rules by priority (severity and version)."""
        def priority_key(rule):
            severity_order = {
                SeverityLevel.CRITICAL.value: 4,
                SeverityLevel.HIGH.value: 3,
                SeverityLevel.MEDIUM.value: 2,
                SeverityLevel.LOW.value: 1
            }
            severity = rule.get("severity", SeverityLevel.LOW.value)
            version = rule.get("version", 1)
            enabled = rule.get("enabled", True)
            
            # Disabled rules have lowest priority
            if not enabled:
                return (0, 0, 0)
            
            return (severity_order.get(severity, 1), version, rule.get("created_at", ""))
        
        return sorted(rules, key=priority_key, reverse=True)

    def _find_applicable_rules(self, risk: Dict, rules: List[Dict]) -> List[Dict]:
        """Find rules applicable to a specific risk."""
        risk_type = risk.get("type", "")
        applicable_rules = []
        
        for rule in rules:
            if not rule.get("enabled", True):
                continue
            
            rule_type = rule.get("type", "")
            pattern = rule.get("pattern", "")
            
            # Check if rule type matches risk type
            if self._rule_matches_risk_type(rule_type, risk_type):
                applicable_rules.append(rule)
            # Check if pattern matches the risk
            elif pattern and self._pattern_matches_risk(pattern, risk):
                applicable_rules.append(rule)
        
        return applicable_rules

    def _rule_matches_risk_type(self, rule_type: str, risk_type: str) -> bool:
        """Check if a rule type matches a risk type."""
        if not rule_type or not risk_type:
            return False
        
        rule_type_lower = rule_type.lower()
        risk_type_lower = risk_type.lower()
        
        # Direct match
        if rule_type_lower == risk_type_lower:
            return True
        
        # Category matches
        if "pii" in rule_type_lower and "pii" in risk_type_lower:
            return True
        
        if "injection" in rule_type_lower and "injection" in risk_type_lower:
            return True
        
        return False

    def _pattern_matches_risk(self, pattern: str, risk: Dict) -> bool:
        """Check if a regex pattern matches the risk."""
        try:
            match_text = risk.get("match", "")
            if not match_text:
                return False
            
            return bool(re.search(pattern, match_text, re.IGNORECASE))
        except re.error:
            return False

    def _update_action(self, current_action: str, new_action: str) -> str:
        """Update action based on priority (block > redact > warn > allow)."""
        action_priority = {
            ActionType.BLOCK.value: FirewallConstants.ACTION_PRIORITY_BLOCK,
            ActionType.REDACT.value: FirewallConstants.ACTION_PRIORITY_REDACT,
            ActionType.WARN.value: FirewallConstants.ACTION_PRIORITY_WARN,
            ActionType.ALLOW.value: FirewallConstants.ACTION_PRIORITY_ALLOW
        }
        
        current_priority = action_priority.get(current_action, 1)
        new_priority = action_priority.get(new_action, 1)
        
        return new_action if new_priority > current_priority else current_action

    def _apply_redaction(self, text: str, risk: Dict) -> str:
        """Apply redaction to text based on risk information."""
        match = risk.get("match", "")
        start = risk.get("start", -1)
        end = risk.get("end", -1)
        
        if not match:
            return text
        
        # Use position-based redaction if available
        if start >= 0 and end > start:
            return text[:start] + FirewallConstants.REDACTED_TEXT + text[end:]
        
        # Fallback to string replacement
        return text.replace(match, FirewallConstants.REDACTED_TEXT)

    def validate_rule(self, rule: Dict) -> Dict[str, Any]:
        """Validate a rule configuration."""
        errors = []
        warnings = []
        
        # Required fields
        required_fields = ["type", "pattern", "action", "severity"]
        for field in required_fields:
            if not rule.get(field):
                errors.append(f"Missing required field: {field}")
        
        # Validate action
        valid_actions = [
            ActionType.BLOCK.value, 
            ActionType.REDACT.value, 
            ActionType.WARN.value, 
            ActionType.ALLOW.value
        ]
        action = rule.get("action", "")
        if action and action not in valid_actions:
            errors.append(f"Invalid action: {action}. Must be one of {valid_actions}")
        
        # Validate severity
        valid_severities = [
            SeverityLevel.LOW.value, 
            SeverityLevel.MEDIUM.value, 
            SeverityLevel.HIGH.value
        ]
        severity = rule.get("severity", "")
        if severity and severity not in valid_severities:
            errors.append(f"Invalid severity: {severity}. Must be one of {valid_severities}")
        
        # Validate regex pattern
        pattern = rule.get("pattern", "")
        if pattern:
            try:
                re.compile(pattern)
            except re.error as e:
                errors.append(f"Invalid regex pattern: {str(e)}")
        
        # Validate version
        version = rule.get("version", 1)
        if not isinstance(version, int) or version < 1:
            warnings.append("Version should be a positive integer")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings
        }

    def create_rule_from_risk(self, risk: Dict, action: str = None, severity: str = None) -> Dict:
        """Create a rule from a detected risk."""
        risk_type = risk.get("type", "CUSTOM")
        match = risk.get("match", "")
        
        # Create a simple pattern from the match
        pattern = re.escape(match) if match else ""
        
        return {
            "type": risk_type,
            "pattern": pattern,
            "action": action or risk.get("action", ActionType.WARN.value),
            "severity": severity or risk.get("severity", SeverityLevel.MEDIUM.value),
            "description": f"Auto-generated rule for {risk_type} detection",
            "enabled": True,
            "version": 1,
            "created_at": datetime.now(timezone.utc).isoformat()
        }

    def merge_rules(self, existing_rules: List[Dict], new_rules: List[Dict]) -> List[Dict]:
        """Merge new rules with existing rules, handling conflicts."""
        merged_rules = existing_rules.copy()
        
        for new_rule in new_rules:
            # Check for conflicts with existing rules
            conflicting_rules = []
            for i, existing_rule in enumerate(merged_rules):
                if self._rules_conflict(existing_rule, new_rule):
                    conflicting_rules.append(i)
            
            # Remove conflicting rules
            for i in reversed(conflicting_rules):
                merged_rules.pop(i)
            
            # Add new rule
            merged_rules.append(new_rule)
        
        return merged_rules

    def _rules_conflict(self, rule1: Dict, rule2: Dict) -> bool:
        """Check if two rules conflict."""
        # Rules conflict if they have the same type and pattern
        return (rule1.get("type") == rule2.get("type") and 
                rule1.get("pattern") == rule2.get("pattern"))

    def get_rule_statistics(self, rules: List[Dict]) -> Dict[str, Any]:
        """Get statistics about a set of rules."""
        if not rules:
            return {
                "total_rules": 0,
                "active_rules": 0,
                "inactive_rules": 0,
                "by_type": {},
                "by_action": {},
                "by_severity": {}
            }
        
        stats = {
            "total_rules": len(rules),
            "active_rules": 0,
            "inactive_rules": 0,
            "by_type": {},
            "by_action": {},
            "by_severity": {}
        }
        
        for rule in rules:
            # Count active/inactive
            if rule.get("enabled", True):
                stats["active_rules"] += 1
            else:
                stats["inactive_rules"] += 1
            
            # Count by type
            rule_type = rule.get("type", "unknown")
            stats["by_type"][rule_type] = stats["by_type"].get(rule_type, 0) + 1
            
            # Count by action
            action = rule.get("action", "unknown")
            stats["by_action"][action] = stats["by_action"].get(action, 0) + 1
            
            # Count by severity
            severity = rule.get("severity", "unknown")
            stats["by_severity"][severity] = stats["by_severity"].get(severity, 0) + 1
        
        return stats

    def _generate_structured_reason(self, action: str, risks: List[Dict]) -> str:
        """Generate a concise, category-only reason; avoid leaking sensitive data."""
        if not risks:
            return "No risks detected"
        
        if action == ActionType.ALLOW.value:
            return "Prompt processed successfully - no risks detected"
        
        # Prefer shared categorization helper
        try:
            from ..firewall.detection_patterns import categorize_risk_type
        except Exception:
            def categorize_risk_type(rt: str) -> str:
                up = (rt or "").upper()
                if "INJECTION" in up:
                    return RiskCategoryType.PROMPT_INJECTION.value
                if "PHI" in up:
                    return RiskCategoryType.PHI.value
                if "PCI" in up:
                    return RiskCategoryType.PCI.value
                return RiskCategoryType.PII.value
        
        buckets: Dict[str, Dict[str, Any]] = {
            RiskCategoryType.PROMPT_INJECTION.value: {"label": "Prompt Injection", "count": 0},
            RiskCategoryType.PII.value: {"label": "PII", "count": 0},
            RiskCategoryType.PHI.value: {"label": "PHI", "count": 0},
            RiskCategoryType.PCI.value: {"label": "PCI", "count": 0},
            RiskCategoryType.CUSTOM.value: {"label": "Custom", "count": 0},
            "OTHER": {"label": "Other", "count": 0},
        }
        
        # Count by category; track injection subtypes for more specific messaging
        injection_subtypes: set[str] = set()
        for r in risks:
            rtype = r.get("type", "")
            rsub = (r.get("subtype") or "").strip()
            cat = r.get("category") or categorize_risk_type(rtype)
            cat = cat if cat in buckets else "OTHER"
            buckets[cat]["count"] += 1
            if cat == RiskCategoryType.PROMPT_INJECTION.value and rsub:
                injection_subtypes.add(rsub)
        
        # Compose single-line generic reason
        action_word = (
            "blocked" if action == ActionType.BLOCK.value else
            "redacted" if action == ActionType.REDACT.value else
            "flagged"
        )
        parts = []
        if buckets[RiskCategoryType.PROMPT_INJECTION.value]["count"]:
            parts.append(f"Prompt Injection ({buckets[RiskCategoryType.PROMPT_INJECTION.value]['count']})")
        if buckets[RiskCategoryType.PII.value]["count"]:
            parts.append(f"PII ({buckets[RiskCategoryType.PII.value]['count']})")
        if buckets[RiskCategoryType.PHI.value]["count"]:
            parts.append(f"PHI ({buckets[RiskCategoryType.PHI.value]['count']})")
        if buckets[RiskCategoryType.PCI.value]["count"]:
            parts.append(f"PCI ({buckets[RiskCategoryType.PCI.value]['count']})")
        if buckets[RiskCategoryType.CUSTOM.value]["count"]:
            parts.append(f"Custom ({buckets[RiskCategoryType.CUSTOM.value]['count']})")
        if buckets["OTHER"]["count"]:
            parts.append(f"Other ({buckets['OTHER']['count']})")

        # If prompt injection is present, prefer a more specific message listing injection types (no matches)
        inj_count = buckets[RiskCategoryType.PROMPT_INJECTION.value]["count"]
        if inj_count > 0:
            types_str = ", ".join(sorted(injection_subtypes)) if injection_subtypes else "unspecified"
            # Optionally include other category counts generically
            others = [p for p in parts if not p.lower().startswith("prompt injection")]
            suffix = f"; also detected: {', '.join(others)}" if others else ""
            return f"Prompt has been {action_word} due to Prompt Injection — types: {types_str}{suffix}"

        detected = ", ".join(parts) if parts else "no risks"
        return f"Prompt has been {action_word} due to: {detected}"
