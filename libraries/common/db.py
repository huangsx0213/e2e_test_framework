from typing import List, Dict, Any, Optional, Type
from abc import ABC, abstractmethod
import cx_Oracle
import psycopg2
from psycopg2.extras import RealDictCursor
from psycopg2.pool import ThreadedConnectionPool
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

    @contextmanager
    def transaction(self):
        """Context manager for handling transactions"""
        try:
            yield
            self.connection.commit()
        except Exception as e:
            self.connection.rollback()
            raise DatabaseError(f"Transaction failed: {str(e)}")


class OracleDatabase(Database):
    def __init__(self):
        self.pool = None
        self.connection = None

    def connect(self, user: str, password: str, host: str, port: int, service_name: str, min_connections: int = 1, max_connections: int = 10):
        try:
            dsn = cx_Oracle.makedsn(host, port, service_name=service_name)
            self.pool = cx_Oracle.SessionPool(user, password, dsn, min=min_connections, max=max_connections, increment=1, threaded=True)
        except cx_Oracle.Error as e:
            raise DatabaseError(f"Failed to create connection pool for Oracle: {str(e)}")

    def _get_connection(self):
        if not self.pool:
            raise DatabaseError("Connection pool not initialized")
        try:
            return self.pool.acquire()
        except cx_Oracle.Error as e:
            raise DatabaseError(f"Failed to acquire connection from pool: {str(e)}")

    def _release_connection(self):
        if self.connection:
            self.pool.release(self.connection)
            self.connection = None

    def disconnect(self):
        if self.pool:
            try:
                self.pool.close()
            finally:
                self.pool = None

    def execute_query(self, table: str, fields: Optional[List[str]] = None, where: Optional[str] = None) -> List[Dict]:
        if fields:
            field_str = ', '.join(fields)
        else:
            field_str = '*'

        query = f"SELECT {field_str} FROM {table}"
        if where:
            query += f" WHERE {where}"

        connection = self._get_connection()
        try:
            with connection.cursor() as cursor:
                try:
                    cursor.execute(query)
                    if fields:
                        return [{field: row[fields.index(field)] for field in fields} for row in cursor]
                    else:
                        return [dict(zip([desc[0].lower() for desc in cursor.description], row))
                                for row in cursor.fetchall()]
                except cx_Oracle.Error as e:
                    raise DatabaseError(f"Query execution failed: {str(e)}")
        finally:
            self._release_connection()

    def update(self, table: str, values: Dict, where: Optional[str] = None) -> bool:
        update_clause = ", ".join([f"{key} = :{key}" for key in values.keys()])
        query = f"UPDATE {table} SET {update_clause}"
        if where:
            query += f" WHERE {where}"

        connection = self._get_connection()
        try:
            with connection.cursor() as cursor:
                try:
                    cursor.execute(query, values)
                    connection.commit()
                    return True
                except cx_Oracle.Error as e:
                    connection.rollback()
                    raise DatabaseError(f"Update failed: {str(e)}")
        finally:
            self._release_connection()

    def insert(self, table: str, data: List[Dict]) -> int:
        if not data:
            return 0

        columns = ', '.join(data[0].keys())
        placeholders = ', '.join([':' + key for key in data[0].keys()])
        query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"

        connection = self._get_connection()
        try:
            with connection.cursor() as cursor:
                try:
                    cursor.executemany(query, data)
                    connection.commit()
                    return cursor.rowcount
                except cx_Oracle.Error as e:
                    connection.rollback()
                    raise DatabaseError(f"Insert failed: {str(e)}")
        finally:
            self._release_connection()


class PostgreSQLDatabase(Database):
    def __init__(self):
        self.pool = None
        self.connection = None

    def connect(self, user: str, password: str, host: str, port: int, database: str, minconn: int = 1, maxconn: int = 10):
        try:
            self.pool = ThreadedConnectionPool(minconn, maxconn,
                                                             user=user, password=password,
                                                             host=host, port=port, database=database)
        except psycopg2.Error as e:
            raise DatabaseError(f"Failed to create connection pool for PostgreSQL: {str(e)}")

    def _get_connection(self):
        if not self.pool:
            raise DatabaseError("Connection pool not initialized")
        try:
            return self.pool.getconn()
        except psycopg2.Error as e:
            raise DatabaseError(f"Failed to acquire connection from pool: {str(e)}")

    def _release_connection(self, connection):
        if connection:
            self.pool.putconn(connection)

    def disconnect(self):
        if self.pool:
            try:
                self.pool.closeall()
            except psycopg2.Error:
                pass  # Ignore if already closed or if there's an error during close

    def execute_query(self, table: str, fields: Optional[List[str]] = None, where: Optional[str] = None) -> List[Dict]:
        if fields:
            field_str = ', '.join(fields)
        else:
            field_str = '*'

        query = f"SELECT {field_str} FROM {table}"
        if where:
            query += f" WHERE {where}"

        connection = self._get_connection()
        try:
            with connection.cursor(cursor_factory=RealDictCursor) as cursor:
                try:
                    cursor.execute(query)
                    if fields:
                        return [dict((k, row[k]) for k in fields if k in row)
                                for row in cursor.fetchall()]
                    return cursor.fetchall()
                except psycopg2.Error as e:
                    raise DatabaseError(f"Query execution failed: {str(e)}")
        finally:
            self._release_connection(connection)

    def update(self, table: str, values: Dict, where: Optional[str] = None) -> bool:
        update_clause = ", ".join([f"{key} = %({key})s" for key in values.keys()])
        query = f"UPDATE {table} SET {update_clause}"
        if where:
            query += f" WHERE {where}"

        connection = self._get_connection()
        try:
            with connection.cursor() as cursor:
                try:
                    cursor.execute(query, values)
                    connection.commit()
                    return True
                except psycopg2.Error as e:
                    connection.rollback()
                    raise DatabaseError(f"Update failed: {str(e)}")
        finally:
            self._release_connection(connection)

    def insert(self, table: str, data: List[Dict]) -> int:
        if not data:
            return 0

        columns = ', '.join(data[0].keys())
        placeholders = ', '.join(['%(' + key + ')s' for key in data[0].keys()])
        query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"

        connection = self._get_connection()
        try:
            with connection.cursor() as cursor:
                try:
                    cursor.executemany(query, data)
                    connection.commit()
                    return cursor.rowcount
                except psycopg2.Error as e:
                    connection.rollback()
                    raise DatabaseError(f"Insert failed: {str(e)}")
        finally:
            self._release_connection(connection)


def get_database(db_type: str) -> Type[Database]:
    """Factory function to get the appropriate database class"""
    databases = {
        'oracle': OracleDatabase,
        'postgresql': PostgreSQLDatabase
    }
    if db_type.lower() not in databases:
        raise ValueError(f"Unsupported database type: {db_type}")
    return databases[db_type.lower()]


def create_database(db_type: str, **kwargs) -> Database:
    """Factory function to create and connect to a database"""
    DatabaseClass = get_database(db_type)
    db = DatabaseClass()
    db.connect(**kwargs)
    return db