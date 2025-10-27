from google.cloud import firestore
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional
import os
from .base import FirestoreBaseStore as Store
from .config import FIRESTORE_CREDENTIALS, PROJECT_ID

class PromptStore(Store):
    """Firestore implementation for prompts table."""
    
    def __init__(self):
        # Use shared client from base class
        super().__init__()
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

    def get_prompt_stats(self, tenant_id: str, days: int = 30) -> Dict:
        """Get prompt statistics for a tenant.
        
        Optimized to only query recent prompts to avoid full collection scans.
        
        Args:
            tenant_id: Tenant ID
            days: Number of days to look back (default 30)
            
        Returns:
            Dictionary with prompt statistics
        """
        # Only query recent prompts to avoid full collection scans
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)
        prompts_ref = self.db.collection(self.collection).document(tenant_id).collection("prompts")
        
        # Query with date filter to limit scope
        query = prompts_ref.where("timestamp", ">=", cutoff_date)
        
        stats = {
            "total_prompts": 0,
            "blocked_prompts": 0,
            "redacted_prompts": 0,
            "warned_prompts": 0,
            "allowed_prompts": 0,
            "pii_detections": 0,
            "injection_detections": 0,
            "avg_anomaly_score": 0.0
        }
        
        # Fetch documents with limited batch size to avoid memory issues
        batch_size = 1000
        docs = []
        for doc in query.stream():
            docs.append(doc.to_dict())
            if len(docs) >= batch_size:
                # Process batch
                for data in docs:
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
                    
                    stats["avg_anomaly_score"] += data.get("anomaly_score", 0.0)
                # Reset for next batch
                docs = []
        
        # Process remaining docs
        for data in docs:
            decision = data.get("decision", "allow")
            if decision == "block":
                stats["blocked_prompts"] += 1
            elif decision == "redact":
                stats["redacted_prompts"] += 1
            elif decision == "warn":
                stats["warned_prompts"] += 1
            else:
                stats["allowed_prompts"] += 1
            
            risks = data.get("risks", [])
            for risk in risks:
                risk_type = risk.get("type", "").lower()
                if "pii" in risk_type:
                    stats["pii_detections"] += 1
                elif "injection" in risk_type:
                    stats["injection_detections"] += 1
            
            stats["avg_anomaly_score"] += data.get("anomaly_score", 0.0)
        
        stats["total_prompts"] = stats["blocked_prompts"] + stats["redacted_prompts"] + stats["warned_prompts"] + stats["allowed_prompts"]
        
        if stats["total_prompts"] > 0:
            stats["avg_anomaly_score"] /= stats["total_prompts"]
        
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
    
    def get_batch(self, tenant_id: str, prompt_ids: List[str]) -> Dict[str, Dict]:
        """Batch fetch multiple prompts by their IDs.
        
        Args:
            tenant_id: Tenant ID
            prompt_ids: List of prompt IDs to fetch
            
        Returns:
            Dictionary mapping prompt_id to prompt data
        """
        if not prompt_ids:
            return {}
        
        # Remove duplicates
        prompt_ids = list(set(prompt_ids))
        
        # Fetch documents in batch
        prompts_ref = self.db.collection(self.collection).document(tenant_id).collection("prompts")
        results = {}
        
        # Firestore batch get (up to 10 docs at a time per Firestore limits)
        batch_size = 10
        for i in range(0, len(prompt_ids), batch_size):
            batch_ids = prompt_ids[i:i+batch_size]
            # Get references for this batch
            refs = [prompts_ref.document(prompt_id) for prompt_id in batch_ids]
            
            # Batch get
            docs = self.db.get_all(refs)
            for doc in docs:
                if doc.exists:
                    data = doc.to_dict()
                    # Convert Firestore timestamp to ISO string
                    if 'timestamp' in data:
                        data['timestamp'] = data['timestamp'].isoformat()
                    results[doc.id] = data
        
        return results
