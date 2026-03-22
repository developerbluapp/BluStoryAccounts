from abc import ABC, abstractmethod
from uuid import UUID
from typing import Optional,  Dict, Any,List

class DatabaseProvider(ABC):
    """Low-level CRUD operations – table/ collection agnostic"""

    @abstractmethod
    def insert(self, table: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Returns the inserted row"""
        pass

    @abstractmethod
    def select_one(
        self,
        table: str,
        filters: Dict[str, Any],
        select_columns: str | List[str] = "*",
    ) -> Optional[Dict[str, Any]]:
        pass

    @abstractmethod
    def select_many(
        self,
        table: str,
        filters: Dict[str, Any],
        select_columns: str | List[str] = "*",
        order_by: Optional[List[tuple[str, str]]] = None,
        limit: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    def update(
        self,
        table: str,
        filters: Dict[str, Any],
        data: Dict[str, Any],
    ) -> List[Dict[str, Any]]:   # returns updated rows
        pass

    @abstractmethod
    def delete(self, table: str, filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        pass