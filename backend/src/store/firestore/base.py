from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any

class Store(ABC):
    """Base class for all store implementations."""
    
    def __init__(self):
        """Initialize the store."""
        pass
    
    @abstractmethod
    def create(self, data: Dict[str, Any]) -> str:
        """Create a new record."""
        pass
    
    @abstractmethod
    def get(self, id: str) -> Optional[Dict[str, Any]]:
        """Get a record by ID."""
        pass
    
    @abstractmethod
    def update(self, id: str, data: Dict[str, Any]) -> bool:
        """Update a record."""
        pass
    
    @abstractmethod
    def delete(self, id: str) -> bool:
        """Delete a record."""
        pass
    
    @abstractmethod
    def query(self, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Query records with optional filters."""
        pass
