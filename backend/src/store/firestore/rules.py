from google.cloud import firestore
from datetime import datetime
from typing import Dict, List, Optional
import os
from .base import FirestoreBaseStore as Store
from .config import FIRESTORE_CREDENTIALS, PROJECT_ID

class RuleStore(Store):
    """Firestore implementation for rules table."""
    
    def __init__(self):
        # Use shared client from base class
        super().__init__()
        self.collection = "tenants"

    def create(self, data: Dict) -> str:
        """Create a new rule (required by base class)."""
        tenant_id = data.get("tenant_id", "")
        if not tenant_id:
            raise ValueError("tenant_id is required")
        return self.save(tenant_id, data)
    
    def save(self, tenant_id: str, data: Dict) -> str:
        """Save a rule for a tenant."""
        rule_ref = self.db.collection(self.collection).document(tenant_id).collection("rules").document()
        
        # Prepare rule data
        rule_data = {
            "rule_id": rule_ref.id,
            "type": data.get("type", "PII"),
            "pattern": data.get("pattern", ""),
            "action": data.get("action", "warn"),
            "severity": data.get("severity", "medium"),
            "version": data.get("version", 1),
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "enabled": data.get("enabled", True),
            "description": data.get("description", ""),
            "metadata": data.get("metadata", {})
        }
        
        rule_ref.set(rule_data)
        return rule_ref.id

    def get(self, id: str) -> Optional[Dict]:
        """Get a rule by ID (required by base class)."""
        raise NotImplementedError("Use get(tenant_id, rule_id) instead")
    
    def get_by_tenant(self, tenant_id: str, rule_id: str) -> Optional[Dict]:
        """Retrieve a rule by ID."""
        rule_ref = self.db.collection(self.collection).document(tenant_id).collection("rules").document(rule_id)
        doc = rule_ref.get()
        
        if doc.exists:
            data = doc.to_dict()
            # Convert Firestore timestamps to ISO strings
            if 'created_at' in data:
                data['created_at'] = data['created_at'].isoformat()
            if 'updated_at' in data:
                data['updated_at'] = data['updated_at'].isoformat()
            return data
        return None

    def query(self, filters: Dict = None) -> List[Dict]:
        """Query rules (required by base class)."""
        raise NotImplementedError("Use query(tenant_id, filters) instead")
    
    def query_by_tenant(self, tenant_id: str, filters: Dict = None) -> List[Dict]:
        """Query rules with optional filters."""
        query = self.db.collection(self.collection).document(tenant_id).collection("rules")
        
        if filters:
            for key, value in filters.items():
                if key == "type":
                    query = query.where("type", "==", value)
                elif key == "action":
                    query = query.where("action", "==", value)
                elif key == "severity":
                    query = query.where("severity", "==", value)
                elif key == "enabled":
                    query = query.where("enabled", "==", value)
                elif key == "version":
                    query = query.where("version", "==", value)
                else:
                    query = query.where(key, "==", value)
        
        # Note: Removed order_by to avoid Firestore index requirement
        # If ordering is needed, create the composite index first
        
        results = []
        for doc in query.stream():
            data = doc.to_dict()
            # Convert Firestore timestamps to ISO strings
            if 'created_at' in data:
                data['created_at'] = data['created_at'].isoformat()
            if 'updated_at' in data:
                data['updated_at'] = data['updated_at'].isoformat()
            results.append(data)
        
        return results

    def update(self, id: str, data: Dict) -> bool:
        """Update a rule (required by base class)."""
        raise NotImplementedError("Use update(tenant_id, rule_id, data) instead")
    
    def update_by_tenant(self, tenant_id: str, rule_id: str, data: Dict) -> bool:
        """Update a rule record."""
        try:
            rule_ref = self.db.collection(self.collection).document(tenant_id).collection("rules").document(rule_id)
            
            # Prepare update data
            update_data = {
                "updated_at": datetime.utcnow()
            }
            
            # Add provided fields
            for key, value in data.items():
                if key not in ["rule_id", "created_at"]:
                    update_data[key] = value
            
            rule_ref.update(update_data)
            return True
        except Exception as e:
            print(f"Error updating rule {rule_id}: {e}")
            return False

    def delete(self, id: str) -> bool:
        """Delete a rule (required by base class)."""
        raise NotImplementedError("Use delete(tenant_id, rule_id) instead")
    
    def delete_by_tenant(self, tenant_id: str, rule_id: str) -> bool:
        """Delete a rule record."""
        try:
            rule_ref = self.db.collection(self.collection).document(tenant_id).collection("rules").document(rule_id)
            rule_ref.delete()
            return True
        except Exception as e:
            print(f"Error deleting rule {rule_id}: {e}")
            return False

    def get_active_rules(self, tenant_id: str) -> List[Dict]:
        """Get all active rules for a tenant."""
        return self.query_by_tenant(tenant_id, {"enabled": True})

    def get_rules_by_type(self, tenant_id: str, rule_type: str) -> List[Dict]:
        """Get rules by type (PII, injection, etc.)."""
        return self.query_by_tenant(tenant_id, {"type": rule_type})

    def get_rules_by_action(self, tenant_id: str, action: str) -> List[Dict]:
        """Get rules by action (block, redact, warn)."""
        return self.query_by_tenant(tenant_id, {"action": action})

    def create_default_rules(self, tenant_id: str) -> List[str]:
        """Create default rules for a new tenant."""
        default_rules = [
            {
                "type": "PII",
                "pattern": r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",
                "action": "redact",
                "severity": "high",
                "description": "Email address detection",
                "enabled": True
            },
            {
                "type": "PII",
                "pattern": r"\b\d{3}-\d{2}-\d{4}\b",
                "action": "block",
                "severity": "high",
                "description": "SSN detection",
                "enabled": True
            },
            {
                "type": "PII",
                "pattern": r"\b\d{3}-\d{3}-\d{4}\b",
                "action": "redact",
                "severity": "medium",
                "description": "Phone number detection",
                "enabled": True
            },
            {
                "type": "injection",
                "pattern": r"(ignore|forget|disregard).*(previous|prior|instructions|rules)",
                "action": "block",
                "severity": "high",
                "description": "Prompt injection attempt",
                "enabled": True
            },
            {
                "type": "injection",
                "pattern": r"(you are|act as|pretend to be|roleplay)",
                "action": "warn",
                "severity": "medium",
                "description": "Role-playing attempt",
                "enabled": True
            }
        ]
        
        created_rule_ids = []
        for rule_data in default_rules:
            rule_id = self.save(tenant_id, rule_data)
            created_rule_ids.append(rule_id)
        
        return created_rule_ids

    def get_rule_stats(self, tenant_id: str) -> Dict:
        """Get rule statistics for a tenant."""
        rules_ref = self.db.collection(self.collection).document(tenant_id).collection("rules")
        
        # Get all rules
        all_rules = list(rules_ref.stream())
        
        stats = {
            "total_rules": len(all_rules),
            "active_rules": 0,
            "inactive_rules": 0,
            "pii_rules": 0,
            "injection_rules": 0,
            "block_rules": 0,
            "redact_rules": 0,
            "warn_rules": 0,
            "high_severity_rules": 0,
            "medium_severity_rules": 0,
            "low_severity_rules": 0
        }
        
        for doc in all_rules:
            data = doc.to_dict()
            
            if data.get("enabled", True):
                stats["active_rules"] += 1
            else:
                stats["inactive_rules"] += 1
            
            rule_type = data.get("type", "").lower()
            if "pii" in rule_type:
                stats["pii_rules"] += 1
            elif "injection" in rule_type:
                stats["injection_rules"] += 1
            
            action = data.get("action", "").lower()
            if action == "block":
                stats["block_rules"] += 1
            elif action == "redact":
                stats["redact_rules"] += 1
            elif action == "warn":
                stats["warn_rules"] += 1
            
            severity = data.get("severity", "").lower()
            if severity == "high":
                stats["high_severity_rules"] += 1
            elif severity == "medium":
                stats["medium_severity_rules"] += 1
            elif severity == "low":
                stats["low_severity_rules"] += 1
        
        return stats

    def bulk_update_rules(self, tenant_id: str, rule_updates: List[Dict]) -> Dict:
        """Bulk update multiple rules."""
        results = {
            "successful": 0,
            "failed": 0,
            "errors": []
        }
        
        for update_data in rule_updates:
            rule_id = update_data.get("rule_id")
            if not rule_id:
                results["failed"] += 1
                results["errors"].append("Missing rule_id in update data")
                continue
            
            if self.update(tenant_id, rule_id, update_data):
                results["successful"] += 1
            else:
                results["failed"] += 1
                results["errors"].append(f"Failed to update rule {rule_id}")
        
        return results
