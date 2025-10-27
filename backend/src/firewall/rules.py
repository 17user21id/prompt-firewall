"""
FirewallRules - Rule application engine for processing detected risks.
Applies tenant-specific rules and policies to determine final actions.
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
import re

class FirewallRules:
    """Applies rules to determine firewall actions."""
    
    def __init__(self):
        self.default_actions = {
            "block": ["block", "deny", "reject"],
            "redact": ["redact", "mask", "hide", "remove"],
            "warn": ["warn", "alert", "notify"],
            "allow": ["allow", "permit", "pass"]
        }

    def apply(self, prompt: str, risks: List[Dict], rules: List[Dict]) -> Dict:
        """Apply tenant-specific rules to the prompt and detected risks."""
        if not risks:
            return {
                "action": "allow",
                "modified": prompt,
                "risks": [],
                "timestamp": datetime.utcnow().isoformat(),
                "reason": "No risks detected",
                "applied_rules": []
            }
        
        # Sort rules by priority (severity and version)
        sorted_rules = self._sort_rules_by_priority(rules)
        
        # Apply rules to determine final action
        final_action = "allow"
        modified_prompt = prompt
        applied_rules = []
        reason_parts = []
        
        for risk in risks:
            risk_type = risk.get("type", "")
            risk_severity = risk.get("severity", "low")
            risk_action = risk.get("action", "warn")
            
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
                if rule_action == "redact":
                    modified_prompt = self._apply_redaction(modified_prompt, risk)
                    reason_parts.append(f"Redacted {risk_type}: {risk.get('match', '')}")
                elif rule_action == "block":
                    modified_prompt = ""
                    reason_parts.append(f"Blocked {risk_type}: {risk.get('match', '')}")
                elif rule_action == "warn":
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
                
                if risk_action == "redact":
                    modified_prompt = self._apply_redaction(modified_prompt, risk)
                    reason_parts.append(f"Redacted {risk_type}: {risk.get('match', '')}")
                elif risk_action == "block":
                    modified_prompt = ""
                    reason_parts.append(f"Blocked {risk_type}: {risk.get('match', '')}")
                elif risk_action == "warn":
                    reason_parts.append(f"Warning for {risk_type}: {risk.get('match', '')}")
        
        # Generate final reason - structured format
        reason = self._generate_structured_reason(final_action, risks)
        
        return {
            "action": final_action,
            "modified": modified_prompt,
            "risks": risks,
            "timestamp": datetime.utcnow().isoformat(),
            "reason": reason,
            "applied_rules": applied_rules,
            "total_rules_applied": len(applied_rules)
        }

    def _sort_rules_by_priority(self, rules: List[Dict]) -> List[Dict]:
        """Sort rules by priority (severity and version)."""
        def priority_key(rule):
            severity_order = {"high": 3, "medium": 2, "low": 1}
            severity = rule.get("severity", "low")
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
        action_priority = {"block": 4, "redact": 3, "warn": 2, "allow": 1}
        
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
            return text[:start] + "[REDACTED]" + text[end:]
        
        # Fallback to string replacement
        return text.replace(match, "[REDACTED]")

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
        valid_actions = ["block", "redact", "warn", "allow"]
        action = rule.get("action", "")
        if action and action not in valid_actions:
            errors.append(f"Invalid action: {action}. Must be one of {valid_actions}")
        
        # Validate severity
        valid_severities = ["low", "medium", "high"]
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
            "action": action or risk.get("action", "warn"),
            "severity": severity or risk.get("severity", "medium"),
            "description": f"Auto-generated rule for {risk_type} detection",
            "enabled": True,
            "version": 1,
            "created_at": datetime.utcnow().isoformat()
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
        """Generate a user-friendly structured reason from detected risks."""
        if not risks:
            return "No risks detected"
        
        if action == "allow":
            return "Prompt processed successfully - no risks detected"
        
        # Group risks by category
        categories = {
            "PROMPT_INJECTION": {"name": "Prompt Injection", "matches": []},
            "PII": {"name": "PII (Personally Identifiable Information)", "matches": []},
            "PHI": {"name": "PHI (Protected Health Information)", "matches": []},
            "PCI": {"name": "PCI (Payment Card Information)", "matches": []},
            "CUSTOM": {"name": "Custom Pattern", "matches": []},
            "OTHER": {"name": "Other", "matches": []}
        }
        
        # First pass: Collect unique matches and their categories
        seen_matches = {}  # {match: [categories]}
        
        for risk in risks:
            risk_type = risk.get("type", "")
            match = risk.get("match", "")
            
            if not match or len(match) > 100:
                continue
            
            # Determine category
            category = "OTHER"
            if "INJECTION" in risk_type:
                category = "PROMPT_INJECTION"
            elif "PHI" in risk_type or risk.get("category") == "PHI":
                category = "PHI"
            elif "PCI" in risk_type or risk.get("category") == "PCI":
                category = "PCI"
            elif "PII" in risk_type or risk.get("category") == "PII":
                category = "PII"
            elif "CUSTOM" in risk_type:
                category = "CUSTOM"
            
            # Normalize match text for comparison (trim and lower)
            normalized_match = match.strip()
            
            # Track matches with their categories
            if normalized_match not in seen_matches:
                seen_matches[normalized_match] = []
            
            if category not in seen_matches[normalized_match]:
                seen_matches[normalized_match].append(category)
        
        # Second pass: Add unique matches to their primary category (first occurrence)
        for match, match_categories in seen_matches.items():
            if match_categories:
                primary_category = match_categories[0]
                truncated_match = match[:80] + "..." if len(match) > 80 else match
                categories[primary_category]["matches"].append(truncated_match)
        
        # Build the structured message
        action_word = "blocked" if action == "block" else "redacted" if action == "redact" else "flagged"
        
        # Collect categories with matches
        found_categories = []
        for cat_key, cat_info in categories.items():
            if cat_info["matches"]:
                found_categories.append(f"{cat_info['name']} ({len(cat_info['matches'])} match{'es' if len(cat_info['matches']) > 1 else ''})")
        
        if found_categories:
            reason = f"Prompt has been {action_word} due to the following entities: {', '.join(found_categories)}"
            
            # Add unique matches for each category (limit to 3 per category)
            for cat_key, cat_info in categories.items():
                if cat_info["matches"]:
                    # Limit matches to avoid huge reasons
                    display_matches = cat_info["matches"][:3]
                    matches_str = "; ".join([f'"{m}"' for m in display_matches])
                    if len(cat_info["matches"]) > 3:
                        matches_str += f" and {len(cat_info['matches']) - 3} more"
                    reason += f"\n{cat_info['name']}: {matches_str}"
        else:
            reason = f"Prompt has been {action_word}"
        
        return reason
