from google.cloud import firestore
from datetime import datetime
from typing import Dict, List, Optional
import hashlib
import uuid
import os
from .base import Store
from ...common.database_constants import DatabaseConstants
from ...common.auth_constants import AuthConstants
from ...common.firestore_config import FIRESTORE_CREDENTIALS, PROJECT_ID

class TenantStore(Store):
    """Firestore implementation for tenants table."""
    
    def __init__(self):
        # Initialize Firestore client with credentials from config
        self.db = firestore.Client(project=PROJECT_ID, credentials=FIRESTORE_CREDENTIALS)
        self.collection = DatabaseConstants.TENANTS_COLLECTION

    def create(self, data: Dict) -> str:
        """Create a new tenant record."""
        tenant_id = str(uuid.uuid4())
        return self.save(tenant_id, data)
    
    def save(self, tenant_id: str, data: Dict) -> str:
        """Save a tenant record."""
        tenant_ref = self.db.collection(self.collection).document(tenant_id)
        
        # Import auth manager for password hashing and API key encryption
        from ...common.auth import AuthManager
        auth_manager = AuthManager()
        
        # Prepare tenant data
        tenant_data = {
            DatabaseConstants.TENANT_ID_FIELD: tenant_id,
            DatabaseConstants.NAME_FIELD: data.get(DatabaseConstants.NAME_FIELD, ""),
            DatabaseConstants.PASSWORD_FIELD: auth_manager.hash_password(data.get(DatabaseConstants.PASSWORD_FIELD, "")),
            DatabaseConstants.API_KEY_FIELD: auth_manager.hash_api_key(self._generate_api_key()),
            DatabaseConstants.CREATED_AT_FIELD: datetime.utcnow(),
            DatabaseConstants.UPDATED_AT_FIELD: datetime.utcnow(),
            DatabaseConstants.STATUS_FIELD: data.get(DatabaseConstants.STATUS_FIELD, DatabaseConstants.DEFAULT_STATUS),
            DatabaseConstants.METADATA_FIELD: data.get(DatabaseConstants.METADATA_FIELD, DatabaseConstants.DEFAULT_METADATA)
        }
        
        tenant_ref.set(tenant_data)
        return tenant_id

    def get(self, tenant_id: str, record_id: str = None) -> Optional[Dict]:
        """Retrieve a tenant by ID."""
        tenant_ref = self.db.collection(self.collection).document(tenant_id)
        doc = tenant_ref.get()
        
        if doc.exists:
            data = doc.to_dict()
            # Convert Firestore timestamps to ISO strings
            if 'created_at' in data:
                data['created_at'] = data['created_at'].isoformat()
            if 'updated_at' in data:
                data['updated_at'] = data['updated_at'].isoformat()
            return data
        return None

    def query(self, tenant_id: str = None, filters: Dict = None) -> List[Dict]:
        """Query tenants with optional filters."""
        query = self.db.collection(self.collection)
        
        if tenant_id:
            query = query.where("tenant_id", "==", tenant_id)
        
        if filters:
            for key, value in filters.items():
                query = query.where(key, "==", value)
        
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
        
    def get_with_decrypted_api_key(self, tenant_id: str) -> Optional[Dict]:
        """Retrieve a tenant by ID with decrypted API key."""
        tenant = self.get(tenant_id)
        if not tenant:
            return None
        
        # Decrypt the API key for response
        from ...common.auth import AuthManager
        auth_manager = AuthManager()
        tenant[DatabaseConstants.API_KEY_FIELD] = auth_manager.decrypt_api_key(tenant[DatabaseConstants.API_KEY_FIELD])
        
        return tenant

    def update(self, tenant_id: str, record_id: str, data: Dict) -> bool:
        """Update a tenant record."""
        try:
            tenant_ref = self.db.collection(self.collection).document(tenant_id)
            
            # Prepare update data
            update_data = {
                "updated_at": datetime.utcnow()
            }
            
            # Add provided fields
            for key, value in data.items():
                if key not in ["tenant_id", "api_key", "created_at"]:
                    update_data[key] = value
            
            tenant_ref.update(update_data)
            return True
        except Exception as e:
            print(f"Error updating tenant {tenant_id}: {e}")
            return False

    def delete(self, tenant_id: str, record_id: str) -> bool:
        """Delete a tenant record."""
        try:
            tenant_ref = self.db.collection(self.collection).document(tenant_id)
            tenant_ref.delete()
            return True
        except Exception as e:
            print(f"Error deleting tenant {tenant_id}: {e}")
            return False

    def _generate_api_key(self) -> str:
        """Generate a hashed API key for the tenant."""
        raw_key = uuid.uuid4().hex
        return hashlib.sha256(raw_key.encode()).hexdigest()

    def validate_api_key(self, tenant_id: str, api_key: str) -> bool:
        """Validate a tenant's API key."""
        tenant = self.get(tenant_id)
        if tenant and tenant.get("api_key") == api_key:
            return True
        return False

    def get_all_tenants(self) -> List[Dict]:
        """Get all tenants (admin function)."""
        return self.query()

    def get_tenant_stats(self, tenant_id: str) -> Dict:
        """Get tenant statistics."""
        tenant = self.get(tenant_id)
        if not tenant:
            return {}
        
        # Get subcollection counts
        prompts_ref = self.db.collection(self.collection).document(tenant_id).collection("prompts")
        rules_ref = self.db.collection(self.collection).document(tenant_id).collection("rules")
        logs_ref = self.db.collection(self.collection).document(tenant_id).collection("logs")
        
        stats = {
            "tenant_id": tenant_id,
            "name": tenant.get("name", ""),
            "created_at": tenant.get("created_at"),
            "prompts_count": len(list(prompts_ref.stream())),
            "rules_count": len(list(rules_ref.stream())),
            "logs_count": len(list(logs_ref.stream())),
            "status": tenant.get("status", "active")
        }
        
        return stats
