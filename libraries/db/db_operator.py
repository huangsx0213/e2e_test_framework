import logging
import os
import re
from typing import Tuple, Any, Dict, Optional
from libraries.db.db import SQLAlchemyDatabase
from libraries.common.config_manager import ConfigManager
from libraries.common.utility_helpers import PROJECT_ROOT
from libraries.common.variable_generator import VariableGenerator
from robot.libraries.BuiltIn import BuiltIn


class DBOperationError(Exception):
    """Custom exception for DBOperator operations"""
    pass


class SingletonMeta(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]


class DBOperator(metaclass=SingletonMeta):
    def __init__(self):
        if not hasattr(self, '_initialized'):
            try:
                self.db_connections: Dict[str, SQLAlchemyDatabase] = {}
                self.db_configs = self._load_db_configs()
                self.active_environment = self._get_active_environment()
                self._initialize_databases()
                self._initialized = True
            except Exception as e:
                raise DBOperationError(f"Failed to initialize DBOperator: {str(e)}")

    def _load_db_configs(self) -> Dict[str, Any]:
        config_path = os.path.join(PROJECT_ROOT, 'configs', 'db_config.yaml')
        return ConfigManager.load_yaml(config_path)

    def _get_active_environment(self) -> str:
        return BuiltIn().get_variable_value("${active_environment}")

    def _initialize_databases(self):
        env_db_configs = self.db_configs.get('database', {}).get(self.active_environment, {})
        self.db_connections = SQLAlchemyDatabase.create_databases(env_db_configs)

    def get_db_connection(self, db_name: str) -> SQLAlchemyDatabase:
        try:
            db_conn = self.db_connections[db_name]
            return db_conn
        except KeyError:
            raise DBOperationError(f"Database connection '{db_name}' not found")

    def validate_database_value(self, db_name: str, db_clause: str) -> Tuple[bool, str]:
        try:
            db = self.get_db_connection(db_name)
            #db_{db_name}.TableName.FieldName[FilterField1=FilterValue1;FilterField2=FilterValue2][OrderBy=CreateTime]=ExpectedValue
            pattern = r'^db_\w+\.(?P<Table>\w+)\.(?P<Field>\w+)\s*\[(?P<Filters>[^\]]+)\](?:\s*\[(?P<OrderBy>[^\]]+)\])?\s*=\s*(?P<ExpectedValue>.+)$'
            match = re.match(pattern, db_clause)
            if not match:
                raise ValueError(f"Invalid format for validate_database_value: {db_clause}")

            table_name = match.group('Table')
            field_name = match.group('Field')
            filters = match.group('Filters')
            order_by = match.group('OrderBy')
            expected_value = match.group('ExpectedValue').strip()

            where_clause = " AND ".join(f"{f.split('=')[0].strip()} = '{f.split('=')[1].strip()}'" for f in filters.split(';') if '=' in f)
            order_by_clause = f"{order_by.replace('OrderBy=', '').strip()}" if order_by else ""

            logging.info(f"{self.__class__.__name__}: Generated SQL query: SELECT {field_name} FROM {table_name} WHERE {where_clause} ORDER BY {order_by_clause}")

            result = db.execute_query(table_name, fields=[field_name], where=where_clause, order_by=order_by_clause)
            if not result:
                raise AssertionError(f"No data found for field '{field_name}' in table '{db_name}.{table_name}' with filters '{where_clause}' and order '{order_by_clause}'.")

            actual_value = result[0][field_name]
            msg = f"Database validation for '{field_name}' in table '{db_name}.{table_name}'. Expected: '{expected_value}', Actual: '{actual_value}'."
            return actual_value == expected_value, msg

        except Exception as e:
            logging.error(f"{self.__class__.__name__}: Database validation failed: {str(e)}")
            return False, f"Database validation failed: {str(e)}"

    def insert_data(self, db_name: str, table: str, data_template: Dict[str, Any], row_count: int = 1) -> int:
        try:
            db = self.get_db_connection(db_name)
            rows = [self._replace_placeholders(data_template) for _ in range(row_count)]
            if row_count == 1:
                for col, value in rows[0].items():
                    BuiltIn().set_global_variable(f'${{{col}}}', value)

            with db.transaction():
                inserted_count = db.insert(table, rows)
                logging.info(f"{self.__class__.__name__}: Inserted {inserted_count} row(s) into '{table}'")
                return inserted_count

        except Exception as e:
            logging.error(f"{self.__class__.__name__}: Failed to insert data into table '{table}': {str(e)}")
            raise DBOperationError(f"Failed to insert data into table '{table}': {str(e)}")

    def update_data(self, db_name: str, table: str, data_template: Dict[str, Any], where_template: str = "") -> bool:
        try:
            db = self.get_db_connection(db_name)
            update_values = self._replace_placeholders(data_template)
            where_clause = self._replace_placeholders(where_template)

            with db.transaction():
                success = db.update(table, update_values, where=where_clause)
                logging.info(f"{self.__class__.__name__}: Update on '{table}' with {update_values}, where: '{where_clause}', success: {success}")
                return success

        except Exception as e:
            logging.error(f"{self.__class__.__name__}: Failed to update data in table '{table}': {str(e)}")
            raise DBOperationError(f"Failed to update data in table '{table}': {str(e)}")

    def delete_data(self, db_name: str, table: str, where_template: str = "") -> int:
        try:
            db = self.get_db_connection(db_name)
            where_clause = self._replace_placeholders(where_template)

            with db.transaction():
                deleted_count = db.delete(table, where=where_clause)
                logging.info(f"{self.__class__.__name__}: Deleted {deleted_count} row(s) from '{table}', where: '{where_clause}'")
                return deleted_count

        except Exception as e:
            logging.error(f"{self.__class__.__name__}: Failed to delete data from table '{table}': {str(e)}")
            raise DBOperationError(f"Failed to delete data from table '{table}': {str(e)}")

    def _replace_placeholders(self, template: Any, placeholder_cache: Optional[Dict[str, str]] = None) -> Any:
        placeholder_cache = placeholder_cache or {}

        if isinstance(template, str):
            template = self._replace_dynamic_variables(template, placeholder_cache)
            template = self._replace_robot_variables(template)
        elif isinstance(template, dict):
            for key, value in template.items():
                template[key] = self._replace_placeholders(value, placeholder_cache)
        return template

    def _replace_dynamic_variables(self, text: str, placeholder_cache: Dict[str, str]) -> str:
        matches = re.findall(r'\{\{\s*([^}]+?)\s*\}\}', text)
        for match in matches:
            if match not in placeholder_cache:
                try:
                    replaced_value = VariableGenerator.generate_dynamic_value(match.strip())
                    placeholder_cache[match] = str(replaced_value)
                except Exception as e:
                    placeholder_cache[match] = f"{{{{UNKNOWN_{match}}}}}"
                    logging.error(f"{self.__class__.__name__}: Failed to replace dynamic value {match}: {e}")
            text = text.replace(f"{{{{{match}}}}}", placeholder_cache[match])
        return text

    def _replace_robot_variables(self, text: str) -> str:
        matches = re.findall(r'\$\{([^}]+)\}', text)
        for match in matches:
            replaced_value = BuiltIn().get_variable_value(f'${{{match}}}')
            text = text.replace(f"${{{match}}}", str(replaced_value))
        return text