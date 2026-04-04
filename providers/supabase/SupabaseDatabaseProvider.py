
from typing import Any, Dict, List, Optional

from supabase import Client

from blustorymicroservices.blustory_accounts_auth.interfaces.DatabaseProvider import DatabaseProvider


class SupabaseDatabaseProvider(DatabaseProvider):
    def __init__(self, client: Client):
        self.client = client

    def _build_query(self, table: str):
        return self.client.table(table)

    def insert(self, table: str, data: Dict[str, Any]) -> Dict[str, Any]:
        resp = self._build_query(table).insert(data).execute()
        return resp.data[0] if resp else {}

    def select_one(self, table: str, filters: Dict[str, Any],
                   select_columns: str | List[str] = "*") -> Optional[Dict[str, Any]]:
        query = self._build_query(table).select(select_columns if isinstance(select_columns, str) else ", ".join(select_columns))
        for k, v in filters.items():
            query = query.eq(k, v)
        resp = query.maybe_single().execute()
        return resp.data if resp else None

    def select_many(self, table: str, filters: Dict[str, Any],
                    select_columns: str | List[str] = "*",
                    order_by: Optional[List[tuple[str, str]]] = None,
                    limit: Optional[int] = None) -> List[Dict[str, Any]]:
        query = self._build_query(table).select(select_columns if isinstance(select_columns, str) else ", ".join(select_columns))
        for k, v in filters.items():
            query = query.eq(k, v)
        if order_by:
            for col, dir in order_by:
                query = query.order(col, desc=(dir.lower() == "desc"))
        if limit:
            query = query.limit(limit)
        resp = query.execute()
        return resp.data if resp else None

    def update(self, table: str, filters: Dict[str, Any], data: Dict[str, Any]) -> List[Dict[str, Any]]:
        query = self._build_query(table).update(data)
        for k, v in filters.items():
            query = query.eq(k, v)
        resp = query.execute()
        return resp.data

    def delete(self, table: str, filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        query = self._build_query(table).delete()
        for k, v in filters.items():
            query = query.eq(k, v)
        resp = query.execute()
        return resp.data if resp else None