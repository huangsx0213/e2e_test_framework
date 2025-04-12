from typing import List, Dict, Optional, Any
from abc import ABC, abstractmethod
from sqlalchemy import create_engine, Table, MetaData, select, update, insert, delete, text
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager, closing


class DatabaseError(Exception):
    """Custom exception for database operations"""
    pass


class Database(ABC):
    @abstractmethod
    def connect(self, **kwargs) -> None:
        pass

    @abstractmethod
    def disconnect(self) -> None:
        pass

    @abstractmethod
    def execute_query(self, table: str, fields: Optional[List[str]] = None, where: Optional[str] = None) -> List[Dict]:
        pass

    @abstractmethod
    def update(self, table: str, values: Dict, where: Optional[str] = None) -> bool:
        pass

    @abstractmethod
    def insert(self, table: str, data: List[Dict]) -> int:
        pass

    @abstractmethod
    def delete(self, table: str, where: Optional[str] = None) -> int:
        pass

    @contextmanager
    def transaction(self):
        """Context manager for handling transactions"""
        session = self.Session()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            raise DatabaseError(f"Transaction failed: {str(e)}")
        finally:
            session.close()


class SQLAlchemyDatabase(Database):
    def __init__(self):
        self.engine = None
        self.Session = None
        self.metadata = MetaData()
        self.default_schema = None
        self.db_type = None

    @classmethod
    def create_databases(cls, db_configs: Dict[str, Dict[str, Any]]) -> Dict[str, 'SQLAlchemyDatabase']:
        databases = {}
        for db_name, config in db_configs.items():
            db_type = config.pop('type').lower()
            schema = config.pop('schema', None)
            db = cls()
            db.connect(db_type=db_type, schema=schema, **config)
            databases[db_name] = db
        return databases

    def connect(self, user: str, password: str, host: str, port: int, database: str, db_type: str = 'postgresql',
                schema: Optional[str] = None):
        try:
            url = self._build_db_url(user, password, host, port, database, db_type)
            self.default_schema = schema or self._default_schema(db_type, database)
            self.engine = create_engine(url)
            self.Session = sessionmaker(bind=self.engine)
            self.metadata.reflect(bind=self.engine, schema=self.default_schema if db_type != 'mysql' else None)
        except Exception as e:
            raise DatabaseError(f"Failed to create connection to {db_type}: {str(e)}")

    def disconnect(self):
        if self.engine:
            self.engine.dispose()

    def _build_db_url(self, user: str, password: str, host: str, port: int, database: str, db_type: str) -> str:
        if db_type == 'postgresql':
            return f"{db_type}://{user}:{password}@{host}:{port}/{database}"
        elif db_type == 'oracle':
            return f"oracle+cx_oracle://{user}:{password}@{host}:{port}/?service_name={database}"
        elif db_type == 'mysql':
            return f"mysql+pymysql://{user}:{password}@{host}:{port}/{database}"
        else:
            raise ValueError(f"Unsupported database type: {db_type}")

    def _default_schema(self, db_type: str, database: str) -> str:
        if db_type == 'oracle':
            return database.upper()
        elif db_type == 'mysql':
            return database
        return 'public'

    def _get_table(self, table_name: str, schema: Optional[str] = None) -> Table:
        effective_schema = schema or self.default_schema
        if self.db_type == 'mysql' and effective_schema != self.default_schema:
            raise DatabaseError("MySQL does not support switching schemas after connection.")
        table_obj = self.metadata.tables.get(table_name) or Table(table_name, self.metadata, schema=effective_schema, autoload_with=self.engine)
        if table_obj is None:
            raise DatabaseError(f"Table '{table_name}' not found in schema '{effective_schema}'.")
        return table_obj

    def execute_query(self, table: str, fields: Optional[List[str]] = None, where: Optional[str] = None, order_by: Optional[str] = None) -> List[Dict]:
        table_obj = self._get_table(table, self.default_schema)
        columns = self._construct_columns(fields, table_obj)
        stmt = select(*columns).where(text(where)) if where else select(*columns)
        if order_by:
            stmt = stmt.order_by(*self._construct_order_by(order_by, table_obj))
        with closing(self.engine.connect()) as connection:
            return [row._mapping for row in connection.execute(stmt)]

    def _construct_columns(self, fields: Optional[List[str]], table_obj: Table) -> List:
        if fields:
            columns = [table_obj.c[field] for field in fields if field in table_obj.c]
            if len(columns) != len(fields):
                raise ValueError(f"Invalid field(s) specified: {', '.join(set(fields) - set(col.name for col in columns))}")
        else:
            columns = list(table_obj.columns)
        return columns

    def _construct_order_by(self, order_by: str, table_obj: Table) -> List:
        order_clauses = []
        for term in order_by.split(','):
            direction = 'desc' if term.lower().endswith(' desc') else 'asc'
            col_name = term.split()[0]
            if col_name not in table_obj.c:
                raise ValueError(f"Invalid order_by column: {col_name}")
            order_clauses.append(getattr(table_obj.c[col_name], direction)())
        return order_clauses

    def insert(self, table: str, data: List[Dict]) -> int:
        table_obj = self._get_table(table, self.default_schema)
        with closing(self.engine.connect()) as connection, connection.begin() as transaction:
            try:
                result = connection.execute(insert(table_obj).values(data))
                return result.rowcount
            except Exception as e:
                transaction.rollback()
                raise DatabaseError(f"Insert operation failed: {str(e)}")

    def update(self, table: str, values: Dict, where: Optional[str] = None) -> bool:
        table_obj = self._get_table(table, self.default_schema)
        stmt = update(table_obj).values(values).where(text(where)) if where else update(table_obj).values(values)
        with closing(self.engine.connect()) as connection, connection.begin() as transaction:
            try:
                result = connection.execute(stmt)
                return result.rowcount > 0
            except Exception as e:
                transaction.rollback()
                raise DatabaseError(f"Update operation failed: {str(e)}")

    def delete(self, table: str, where: Optional[str] = None) -> int:
        table_obj = self._get_table(table, self.default_schema)
        stmt = delete(table_obj).where(text(where)) if where else delete(table_obj)
        with closing(self.engine.connect()) as connection, connection.begin() as transaction:
            try:
                result = connection.execute(stmt)
                return result.rowcount
            except Exception as e:
                transaction.rollback()
                raise DatabaseError(f"Delete operation failed: {str(e)}")