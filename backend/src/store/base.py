from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional

class Store(ABC):
    """Abstract base class for database operations."""
    
    @abstractmethod
    def save(self, tenant_id: str, data: Dict) -> str:
        """Save a record and return its ID."""
        pass

    @abstractmethod
    def get(self, tenant_id: str, record_id: str) -> Optional[Dict]:
        """Retrieve a record by ID."""
        pass

    @abstractmethod
    def query(self, tenant_id: str, filters: Dict = None) -> List[Dict]:
        """Query records with optional filters."""
        pass

    @abstractmethod
    def update(self, tenant_id: str, record_id: str, data: Dict) -> bool:
        """Update a record by ID."""
        pass

    @abstractmethod
    def delete(self, tenant_id: str, record_id: str) -> bool:
        """Delete a record by ID."""
        pass
