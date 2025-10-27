"""
Base Firestore store class with shared client management.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from google.cloud import firestore
from .config import FIRESTORE_CREDENTIALS, PROJECT_ID

class FirestoreBaseStore(ABC):
    """Base class for Firestore store implementations with shared client."""
    
    # Shared Firestore client across all stores (singleton pattern)
    _db_client = None
    
    @classmethod
    def _get_client(cls):
        """Get or create Firestore client (singleton)."""
        if cls._db_client is None:
            cls._db_client = firestore.Client(
                project=PROJECT_ID, 
                credentials=FIRESTORE_CREDENTIALS
            )
        return cls._db_client
    
    def __init__(self):
        """Initialize the store with shared Firestore client."""
        self.db = self._get_client()
        self.collection = "tenants"
    
    @abstractmethod
    def save(self, tenant_id: str, data: Dict[str, Any]) -> str:
        """Save a record."""
        pass
    
    @abstractmethod
    def get(self, tenant_id: str, record_id: str = None) -> Optional[Dict[str, Any]]:
        """Get a record."""
        pass
    
    @abstractmethod
    def query_by_tenant(self, tenant_id: str, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Query records."""
        pass
    
    @abstractmethod
    def update(self, tenant_id: str, record_id: str, data: Dict[str, Any]) -> bool:
        """Update a record."""
        pass
    
    @abstractmethod
    def delete(self, tenant_id: str, record_id: str) -> bool:
        """Delete a record."""
        pass
