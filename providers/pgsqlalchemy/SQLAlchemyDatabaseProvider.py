from typing import Any, Dict, List, Optional, Type
from sqlalchemy.orm import Session
from sqlalchemy import MetaData, select, update as sa_update, delete as sa_delete

from blustorymicroservices.BluStoryAccounts.providers.interfaces.DatabaseProvider import DatabaseProvider
from typing import Any, Dict, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import Table, select, update as sa_update, delete as sa_delete
from typing import Any, Dict, List, Optional, Union

class SQLAlchemyDatabaseProvider(DatabaseProvider):
    def __init__(self, session: Session, metadata: MetaData):
        self.session = session
        self.metadata = metadata

    def _get_table(self, table_name: str) -> Table:
        # 1. Check if already in metadata
        if table_name in self.metadata.tables:
            return self.metadata.tables[table_name]

        # 2. Parse schema and table name
        # If table_name is "auth.users", schema="auth" and name="users"
        if "." in table_name:
            schema, name = table_name.split(".", 1)
        else:
            schema, name = None, table_name

        # 3. Reflect using the explicit schema argument
        # Note: Use self.session.get_bind() for SQLAlchemy 2.0 compatibility
        return Table(
            name, 
            self.metadata, 
            schema=schema, 
            autoload_with=self.session.get_bind()
        )

    def insert(self, table: str, data: Dict[str, Any]) -> Dict[str, Any]:
        tbl = self._get_table(table)
        stmt = tbl.insert().values(**data).returning(tbl)
        result = self.session.execute(stmt).first()
        self.session.commit()
        # Use ._mapping to convert Row to Dict
        return dict(result._mapping) if result else {}

    def select_one(
        self,
        table: str,
        filters: Dict[str, Any],
        select_columns: Union[str, List[str]] = "*"
    ) -> Optional[Dict[str, Any]]:
        tbl = self._get_table(table)

        if isinstance(select_columns, list):
            stmt = select(*[tbl.c[col] for col in select_columns])
        elif select_columns != "*":
            stmt = select(tbl.c[select_columns])
        else:
            stmt = select(tbl)

        for k, v in filters.items():
            stmt = stmt.where(tbl.c[k] == v)

        result = self.session.execute(stmt).first()
        # Use ._mapping for the dictionary conversion
        return dict(result._mapping) if result else None

    def select_many(
        self,
        table: str,
        filters: Dict[str, Any],
        select_columns: Union[str, List[str]] = "*",
        order_by: Optional[List[tuple[str, str]]] = None,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        tbl = self._get_table(table)

        if isinstance(select_columns, list):
            stmt = select(*[tbl.c[col] for col in select_columns])
        elif select_columns != "*":
            stmt = select(tbl.c[select_columns])
        else:
            stmt = select(tbl)

        for k, v in filters.items():
            stmt = stmt.where(tbl.c[k] == v)

        if order_by:
            for col, direction in order_by:
                column = tbl.c[col]
                stmt = stmt.order_by(column.desc() if direction.lower() == "desc" else column.asc())

        if limit:
            stmt = stmt.limit(limit)

        results = self.session.execute(stmt).all()
        # List comprehension using ._mapping
        return [dict(r._mapping) for r in results]

    def update(
        self,
        table: str,
        filters: Dict[str, Any],
        data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        tbl = self._get_table(table)
        stmt = sa_update(tbl).values(**data).returning(tbl)

        for k, v in filters.items():
            stmt = stmt.where(tbl.c[k] == v)

        results = self.session.execute(stmt).all()
        self.session.commit()
        return [dict(r._mapping) for r in results]

    def delete(
        self,
        table: str,
        filters: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        tbl = self._get_table(table)
        stmt = sa_delete(tbl).returning(tbl)

        for k, v in filters.items():
            stmt = stmt.where(tbl.c[k] == v)

        results = self.session.execute(stmt).all()
        self.session.commit()
        return [dict(r._mapping) for r in results]