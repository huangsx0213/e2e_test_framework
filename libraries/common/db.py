from typing import List, Dict, Optional, Any
from abc import ABC, abstractmethod
from sqlalchemy import create_engine, Table, MetaData, select, update, insert, delete, text
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager


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
        self.default_schema = None  # Store the default schema for the connection
        self.db_type = None

    @classmethod
    def create_databases(cls, db_configs: Dict) -> Dict[str, 'SQLAlchemyDatabase']:
        databases = {}
        for db_name, config in db_configs.items():
            db_type = config.pop('type').lower()
            schema = config.pop('schema', None)
            db = cls()  # Use cls() to create an instance
            db.connect(db_type=db_type, schema=schema, **config)
            databases[db_name] = db
        return databases

    def connect(self, user: str, password: str, host: str, port: int, database: str, db_type: str = 'postgresql',
                schema: Optional[str] = None):
        try:
            self.db_type = db_type
            if db_type == 'postgresql':
                url = f"{db_type}://{user}:{password}@{host}:{port}/{database}"
                self.default_schema = schema or 'public'
            elif db_type == 'oracle':
                url = f"oracle+cx_oracle://{user}:{password}@{host}:{port}/?service_name={database}"
                self.default_schema = schema or user.upper()  # Oracle schema is usually the username in uppercase
            elif db_type == 'mysql':
                url = f"mysql+pymysql://{user}:{password}@{host}:{port}/{database}"
                self.default_schema = schema or database  # In MySQL, schema is often the same as the database
            else:
                raise ValueError(f"Unsupported database type: {db_type}")

            self.engine = create_engine(url)
            self.Session = sessionmaker(bind=self.engine)
            self.metadata.reflect(bind=self.engine, schema=self.default_schema if db_type != 'mysql' else None)  # Reflect only if not MySQL
        except Exception as e:
            raise DatabaseError(f"Failed to create connection to {db_type}: {str(e)}")

    def disconnect(self):
        if self.engine:
            self.engine.dispose()

    def _get_table(self, table_name: str, schema: Optional[str] = None) -> Table:
        """Helper to get Table object, handling schema appropriately."""
        effective_schema = schema or self.default_schema

        if self.db_type == 'mysql':
            # MySQL: No schema handling at the Table level.
            if effective_schema != self.default_schema:
                raise DatabaseError("MySQL does not support switching schemas after connection.")
            table_obj = self.metadata.tables.get(table_name)
        else:
            # PostgreSQL, Oracle, etc.: Use schema if provided, otherwise use default.
            table_obj = Table(table_name, self.metadata, schema=effective_schema, autoload_with=self.engine)

        if table_obj is None:
            raise DatabaseError(f"Table '{table_name}' not found in schema '{effective_schema}'.")
        return table_obj

    def execute_query(self, table: str, fields: Optional[List[str]] = None, where: Optional[str] = None, order_by: Optional[str] = None) -> List[Dict]:
        table_obj = self._get_table(table, self.default_schema)

        # Determine which columns to select
        if fields:
            columns = [table_obj.c[field] for field in fields if field in table_obj.c]
            if len(columns) != len(fields):
                missing_fields = set(fields) - set(col.name for col in columns)
                raise ValueError(f"Invalid field(s) specified: {', '.join(missing_fields)}")
        else:
            columns = [col for col in table_obj.columns]

        stmt = select(*columns)

        if where:
            stmt = stmt.where(text(where))
        if order_by:
            order_clauses = []
            for order_term in order_by.split(','):
                order_term = order_term.strip()
                if order_term.lower().endswith(" desc"):
                    col_name = order_term[:-5].strip()
                    if col_name in table_obj.c:
                        order_clauses.append(table_obj.c[col_name].desc())
                    else:
                        raise ValueError(f"Invalid order_by column: {col_name}")
                elif order_term.lower().endswith(" asc"):
                    col_name = order_term[:-4].strip()
                    if col_name in table_obj.c:
                        order_clauses.append(table_obj.c[col_name].asc())
                    else:
                        raise ValueError(f"Invalid order_by column: {col_name}")
                else:
                    if order_term in table_obj.c:
                        order_clauses.append(table_obj.c[order_term].asc())
                    else:
                        raise ValueError(f"Invalid order_by column: {order_term}")
            stmt = stmt.order_by(*order_clauses)

        with self.engine.connect() as connection:
            result = connection.execute(stmt)

            # Use the Row object's _mapping attribute for dictionary-like access
            return [row._mapping for row in result]

    def insert(self, table: str, data: List[Dict]) -> int:
        table_obj = self._get_table(table, self.default_schema)
        stmt = insert(table_obj).values(data)

        with self.engine.connect() as connection:
            with connection.begin() as transaction:
                try:
                    result = connection.execute(stmt)
                    transaction.commit()
                    return result.rowcount
                except Exception as e:
                    transaction.rollback()
                    raise DatabaseError(f"Insert operation failed: {str(e)}")

    def update(self, table: str, values: Dict, where: Optional[str] = None) -> bool:
        table_obj = self._get_table(table, self.default_schema)
        stmt = update(table_obj).values(values)
        if where:
            stmt = stmt.where(text(where))

        with self.engine.connect() as connection:
            with connection.begin() as transaction:
                try:
                    result = connection.execute(stmt)
                    transaction.commit()  # Commit the transaction
                    return result.rowcount > 0
                except Exception as e:
                    transaction.rollback()  # Rollback if an error occurs
                    raise DatabaseError(f"Update operation failed: {str(e)}")

    def delete(self, table: str, where: Optional[str] = None) -> int:
        table_obj = self._get_table(table, self.default_schema)
        stmt = delete(table_obj)
        if where:
            stmt = stmt.where(text(where))

        with self.engine.connect() as connection:
            with connection.begin() as transaction:
                try:
                    result = connection.execute(stmt)
                    transaction.commit()  # Commit the transaction
                    return result.rowcount
                except Exception as e:
                    transaction.rollback()  # Rollback if an error occurs
                    raise DatabaseError(f"Delete operation failed: {str(e)}")

