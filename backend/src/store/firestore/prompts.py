from google.cloud import firestore
from datetime import datetime
from typing import Dict, List, Optional
import os
from .base import Store
from ...common.firestore_config import FIRESTORE_CREDENTIALS, PROJECT_ID

class PromptStore(Store):
    """Firestore implementation for prompts table."""
    
    def __init__(self):
        # Initialize Firestore client with credentials from config
        self.db = firestore.Client(project=PROJECT_ID, credentials=FIRESTORE_CREDENTIALS)
        self.collection = "tenants"

    def create(self, data: Dict) -> str:
        """Create a new prompt record (required by base class)."""
        tenant_id = data.get("tenant_id", "")
        if not tenant_id:
            raise ValueError("tenant_id is required")
        return self.save(tenant_id, data)
    
    def save(self, tenant_id: str, data: Dict) -> str:
        """Save a prompt record for a tenant."""
        prompt_ref = self.db.collection(self.collection).document(tenant_id).collection("prompts").document()
        
        # Prepare prompt data
        prompt_data = {
            "prompt_id": prompt_ref.id,
            "prompt": data.get("prompt", ""),
            "response": data.get("response", ""),
            "decision": data.get("decision", "allow"),
            "promptModified": data.get("promptModified", ""),
            "risks": data.get("risks", []),
            "anomaly_score": data.get("anomaly_score", 0.0),
            "timestamp": datetime.utcnow(),
            "user_id": data.get("user_id", ""),
            "metadata": data.get("metadata", {})
        }
        
        prompt_ref.set(prompt_data)
        return prompt_ref.id

    def get(self, id: str) -> Optional[Dict]:
        """Get a prompt by ID (required by base class)."""
        # This method signature doesn't match the tenant-specific implementation
        # We'll implement a generic version that requires tenant_id
        raise NotImplementedError("Use get(tenant_id, prompt_id) instead")
    
    def get_by_tenant(self, tenant_id: str, prompt_id: str) -> Optional[Dict]:
        """Retrieve a prompt by ID."""
        prompt_ref = self.db.collection(self.collection).document(tenant_id).collection("prompts").document(prompt_id)
        doc = prompt_ref.get()
        
        if doc.exists:
            data = doc.to_dict()
            # Convert Firestore timestamp to ISO string
            if 'timestamp' in data:
                data['timestamp'] = data['timestamp'].isoformat()
            return data
        return None

    def query(self, filters: Dict = None) -> List[Dict]:
        """Query prompts (required by base class)."""
        # This method signature doesn't match the tenant-specific implementation
        raise NotImplementedError("Use query(tenant_id, filters) instead")
    
    def query_by_tenant(self, tenant_id: str, filters: Dict = None) -> List[Dict]:
        """Query prompts with optional filters."""
        query = self.db.collection(self.collection).document(tenant_id).collection("prompts")
        
        if filters:
            for key, value in filters.items():
                if key == "date_from":
                    query = query.where("timestamp", ">=", datetime.fromisoformat(value))
                elif key == "date_to":
                    query = query.where("timestamp", "<=", datetime.fromisoformat(value))
                elif key == "decision":
                    query = query.where("decision", "==", value)
                elif key == "user_id":
                    query = query.where("user_id", "==", value)
                elif key == "has_risks":
                    if value:
                        query = query.where("risks", "!=", [])
                else:
                    query = query.where(key, "==", value)
        
        # Order by timestamp descending
        query = query.order_by("timestamp", direction=firestore.Query.DESCENDING)
        
        results = []
        for doc in query.stream():
            data = doc.to_dict()
            # Convert Firestore timestamp to ISO string
            if 'timestamp' in data:
                data['timestamp'] = data['timestamp'].isoformat()
            results.append(data)
        
        return results

    def update(self, id: str, data: Dict) -> bool:
        """Update a prompt (required by base class)."""
        raise NotImplementedError("Use update(tenant_id, prompt_id, data) instead")
    
    def update_by_tenant(self, tenant_id: str, prompt_id: str, data: Dict) -> bool:
        """Update a prompt record."""
        try:
            prompt_ref = self.db.collection(self.collection).document(tenant_id).collection("prompts").document(prompt_id)
            
            # Prepare update data
            update_data = {}
            
            # Add provided fields
            for key, value in data.items():
                if key not in ["prompt_id", "timestamp"]:
                    update_data[key] = value
            
            prompt_ref.update(update_data)
            return True
        except Exception as e:
            print(f"Error updating prompt {prompt_id}: {e}")
            return False

    def delete(self, id: str) -> bool:
        """Delete a prompt (required by base class)."""
        raise NotImplementedError("Use delete(tenant_id, prompt_id) instead")
    
    def delete_by_tenant(self, tenant_id: str, prompt_id: str) -> bool:
        """Delete a prompt record."""
        try:
            prompt_ref = self.db.collection(self.collection).document(tenant_id).collection("prompts").document(prompt_id)
            prompt_ref.delete()
            return True
        except Exception as e:
            print(f"Error deleting prompt {prompt_id}: {e}")
            return False

    def get_prompt_stats(self, tenant_id: str) -> Dict:
        """Get prompt statistics for a tenant."""
        prompts_ref = self.db.collection(self.collection).document(tenant_id).collection("prompts")
        
        # Get all prompts
        all_prompts = list(prompts_ref.stream())
        
        stats = {
            "total_prompts": len(all_prompts),
            "blocked_prompts": 0,
            "redacted_prompts": 0,
            "warned_prompts": 0,
            "allowed_prompts": 0,
            "pii_detections": 0,
            "injection_detections": 0,
            "avg_anomaly_score": 0.0
        }
        
        if all_prompts:
            total_score = 0
            for doc in all_prompts:
                data = doc.to_dict()
                decision = data.get("decision", "allow")
                
                if decision == "block":
                    stats["blocked_prompts"] += 1
                elif decision == "redact":
                    stats["redacted_prompts"] += 1
                elif decision == "warn":
                    stats["warned_prompts"] += 1
                else:
                    stats["allowed_prompts"] += 1
                
                # Count risk types
                risks = data.get("risks", [])
                for risk in risks:
                    risk_type = risk.get("type", "").lower()
                    if "pii" in risk_type:
                        stats["pii_detections"] += 1
                    elif "injection" in risk_type:
                        stats["injection_detections"] += 1
                
                # Calculate average anomaly score
                total_score += data.get("anomaly_score", 0.0)
            
            stats["avg_anomaly_score"] = total_score / len(all_prompts)
        
        return stats

    def get_recent_prompts(self, tenant_id: str, limit: int = 10) -> List[Dict]:
        """Get recent prompts for a tenant."""
        query = self.db.collection(self.collection).document(tenant_id).collection("prompts")
        query = query.order_by("timestamp", direction=firestore.Query.DESCENDING).limit(limit)
        
        results = []
        for doc in query.stream():
            data = doc.to_dict()
            # Convert Firestore timestamp to ISO string
            if 'timestamp' in data:
                data['timestamp'] = data['timestamp'].isoformat()
            results.append(data)
        
        return results
