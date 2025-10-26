from google.cloud import firestore
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import os
from .base import Store
from ...common.firestore_config import FIRESTORE_CREDENTIALS, PROJECT_ID

class LogStore(Store):
    """Firestore implementation for logs table."""
    
    def __init__(self):
        # Initialize Firestore client with credentials from config
        self.db = firestore.Client(project=PROJECT_ID, credentials=FIRESTORE_CREDENTIALS)
        self.collection = "tenants"

    def create(self, data: Dict) -> str:
        """Create a new log (required by base class)."""
        tenant_id = data.get("tenant_id", "")
        if not tenant_id:
            raise ValueError("tenant_id is required")
        return self.save(tenant_id, data)
    
    def save(self, tenant_id: str, data: Dict) -> str:
        """Save a log entry for a tenant."""
        log_ref = self.db.collection(self.collection).document(tenant_id).collection("logs").document()
        
        # Prepare log data
        log_data = {
            "log_id": log_ref.id,
            "prompt_id": data.get("prompt_id", ""),
            "event_type": data.get("event_type", "processed"),
            "details": data.get("details", {}),
            "timestamp": datetime.utcnow(),
            "user_id": data.get("user_id", ""),
            "ip_address": data.get("ip_address", ""),
            "user_agent": data.get("user_agent", ""),
            "metadata": data.get("metadata", {})
        }
        
        log_ref.set(log_data)
        return log_ref.id

    def get(self, id: str) -> Optional[Dict]:
        """Get a log by ID (required by base class)."""
        raise NotImplementedError("Use get(tenant_id, log_id) instead")
    
    def get_by_tenant(self, tenant_id: str, log_id: str) -> Optional[Dict]:
        """Retrieve a log by ID."""
        log_ref = self.db.collection(self.collection).document(tenant_id).collection("logs").document(log_id)
        doc = log_ref.get()
        
        if doc.exists:
            data = doc.to_dict()
            # Convert Firestore timestamp to ISO string
            if 'timestamp' in data:
                data['timestamp'] = data['timestamp'].isoformat()
            return data
        return None

    def query(self, filters: Dict = None) -> List[Dict]:
        """Query logs (required by base class)."""
        raise NotImplementedError("Use query(tenant_id, filters) instead")
    
    def query_by_tenant(self, tenant_id: str, filters: Dict = None) -> List[Dict]:
        """Query logs with optional filters."""
        query = self.db.collection(self.collection).document(tenant_id).collection("logs")
        
        if filters:
            for key, value in filters.items():
                if key == "event_type":
                    query = query.where("event_type", "==", value)
                elif key == "date_from":
                    query = query.where("timestamp", ">=", datetime.fromisoformat(value))
                elif key == "date_to":
                    query = query.where("timestamp", "<=", datetime.fromisoformat(value))
                elif key == "user_id":
                    query = query.where("user_id", "==", value)
                elif key == "prompt_id":
                    query = query.where("prompt_id", "==", value)
                elif key == "ip_address":
                    query = query.where("ip_address", "==", value)
                else:
                    query = query.where(key, "==", value)
        
        # Order by timestamp descending
        query = query.order_by("timestamp", direction=firestore.Query.DESCENDING)
        
        # Apply limit if specified
        limit = filters.get("limit", 100) if filters else 100
        query = query.limit(limit)
        
        results = []
        for doc in query.stream():
            data = doc.to_dict()
            # Convert Firestore timestamp to ISO string
            if 'timestamp' in data:
                data['timestamp'] = data['timestamp'].isoformat()
            results.append(data)
        
        return results

    def update(self, id: str, data: Dict) -> bool:
        """Update a log (required by base class)."""
        raise NotImplementedError("Use update(tenant_id, log_id, data) instead")
    
    def update_by_tenant(self, tenant_id: str, log_id: str, data: Dict) -> bool:
        """Update a log record."""
        try:
            log_ref = self.db.collection(self.collection).document(tenant_id).collection("logs").document(log_id)
            
            # Prepare update data
            update_data = {}
            
            # Add provided fields
            for key, value in data.items():
                if key not in ["log_id", "timestamp"]:
                    update_data[key] = value
            
            log_ref.update(update_data)
            return True
        except Exception as e:
            print(f"Error updating log {log_id}: {e}")
            return False

    def delete(self, id: str) -> bool:
        """Delete a log (required by base class)."""
        raise NotImplementedError("Use delete(tenant_id, log_id) instead")
    
    def delete_by_tenant(self, tenant_id: str, log_id: str) -> bool:
        """Delete a log record."""
        try:
            log_ref = self.db.collection(self.collection).document(tenant_id).collection("logs").document(log_id)
            log_ref.delete()
            return True
        except Exception as e:
            print(f"Error deleting log {log_id}: {e}")
            return False

    def get_recent_logs(self, tenant_id: str, limit: int = 50) -> List[Dict]:
        """Get recent logs for a tenant."""
        return self.query(tenant_id, {"limit": limit})

    def get_logs_by_event_type(self, tenant_id: str, event_type: str) -> List[Dict]:
        """Get logs by event type."""
        return self.query(tenant_id, {"event_type": event_type})

    def get_logs_by_date_range(self, tenant_id: str, date_from: str, date_to: str) -> List[Dict]:
        """Get logs within a date range."""
        return self.query(tenant_id, {"date_from": date_from, "date_to": date_to})

    def get_log_stats(self, tenant_id: str, days: int = 30) -> Dict:
        """Get log statistics for a tenant."""
        # Calculate date range
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Get logs within date range
        logs_ref = self.db.collection(self.collection).document(tenant_id).collection("logs")
        logs_query = logs_ref.where("timestamp", ">=", start_date).where("timestamp", "<=", end_date)
        
        all_logs = list(logs_query.stream())
        
        stats = {
            "total_logs": len(all_logs),
            "processed_logs": 0,
            "blocked_logs": 0,
            "redacted_logs": 0,
            "warned_logs": 0,
            "error_logs": 0,
            "unique_users": set(),
            "unique_ips": set(),
            "daily_counts": {},
            "event_type_counts": {}
        }
        
        for doc in all_logs:
            data = doc.to_dict()
            event_type = data.get("event_type", "processed")
            
            # Count by event type
            if event_type == "processed":
                stats["processed_logs"] += 1
            elif event_type == "blocked":
                stats["blocked_logs"] += 1
            elif event_type == "redacted":
                stats["redacted_logs"] += 1
            elif event_type == "warned":
                stats["warned_logs"] += 1
            elif event_type == "error":
                stats["error_logs"] += 1
            
            # Count unique users and IPs
            user_id = data.get("user_id")
            if user_id:
                stats["unique_users"].add(user_id)
            
            ip_address = data.get("ip_address")
            if ip_address:
                stats["unique_ips"].add(ip_address)
            
            # Count by day
            timestamp = data.get("timestamp")
            if timestamp:
                day_key = timestamp.strftime("%Y-%m-%d")
                stats["daily_counts"][day_key] = stats["daily_counts"].get(day_key, 0) + 1
            
            # Count by event type
            stats["event_type_counts"][event_type] = stats["event_type_counts"].get(event_type, 0) + 1
        
        # Convert sets to counts
        stats["unique_users"] = len(stats["unique_users"])
        stats["unique_ips"] = len(stats["unique_ips"])
        
        return stats

    def export_logs(self, tenant_id: str, filters: Dict = None) -> List[Dict]:
        """Export logs for a tenant (for download/backup)."""
        # Remove limit for export
        export_filters = filters.copy() if filters else {}
        export_filters.pop("limit", None)
        
        return self.query(tenant_id, export_filters)

    def cleanup_old_logs(self, tenant_id: str, days_to_keep: int = 90) -> int:
        """Clean up logs older than specified days."""
        cutoff_date = datetime.utcnow() - timedelta(days=days_to_keep)
        
        logs_ref = self.db.collection(self.collection).document(tenant_id).collection("logs")
        old_logs_query = logs_ref.where("timestamp", "<", cutoff_date)
        
        deleted_count = 0
        for doc in old_logs_query.stream():
            doc.reference.delete()
            deleted_count += 1
        
        return deleted_count

    def log_event(self, tenant_id: str, event_type: str, details: Dict, 
                   prompt_id: str = "", user_id: str = "", 
                   ip_address: str = "", user_agent: str = "") -> str:
        """Convenience method to log an event."""
        log_data = {
            "prompt_id": prompt_id,
            "event_type": event_type,
            "details": details,
            "user_id": user_id,
            "ip_address": ip_address,
            "user_agent": user_agent
        }
        
        return self.save(tenant_id, log_data)
