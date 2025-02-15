import logging
import os
import re
from typing import Tuple, Any, Dict
from libraries.common.db import create_database
from libraries.common.config_manager import ConfigManager
from libraries.common.utility_helpers import PROJECT_ROOT
from libraries.common.variable_generator import VariableGenerator
from robot.libraries.BuiltIn import BuiltIn


class SingletonMeta(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]


class DBOperator:

    def __init__(self):
        self.db = None
        self.db_cache = {}
        self.db_configs = self._load_db_configs()
        self.active_environment = self._get_active_environment()

    def _load_db_configs(self) -> Dict[str, Any]:
        config_path = os.path.join(PROJECT_ROOT, 'configs', 'db_config.yaml')
        return ConfigManager.load_yaml(config_path)

    def _get_active_environment(self) -> str:
        return BuiltIn().get_variable_value("${active_environment}")

    def setup_database(self, db_name: str) -> None:
        db_config = self._get_db_config(db_name)
        db_key = self._get_db_key(db_config)

        if db_key in self.db_cache:
            self.db = self.db_cache[db_key]
            logging.info(f"{self.__class__.__name__}: Reusing cached DB connection for {db_key}.")
        else:
            self._create_and_cache_db_connection(db_config, db_key)

    def _get_db_config(self, db_name: str) -> Dict[str, Any]:
        db_config = self.db_configs.get('database', {}).get(self.active_environment, {}).get(db_name.lower(), {})

        if not db_config:
            raise ValueError(
                f"{self.__class__.__name__}: Database configuration not found for {db_name} "
                f"in {self.active_environment} environment."
            )
        return db_config

    def _create_and_cache_db_connection(self, db_config: Dict[str, Any], db_key: str) -> None:
        db_config_copy = db_config.copy()
        db_type = db_config_copy.pop('type').lower()
        self.db = create_database(db_type, **db_config_copy)
        self.db_cache[db_key] = self.db
        logging.info(f"{self.__class__.__name__}: New connection created and cached for {db_key}.")

    def _get_db_key(self, db_config: Dict[str, Any]) -> str:
        db_type = db_config['type'].lower()
        host = db_config.get('host', 'localhost')
        port = db_config.get('port', 3306)
        db_instance_name = db_config.get('database', '')
        return f"{db_type}_{host}_{port}_{db_instance_name}"

    def validate_database_value(self, db_name: str, db_clause: str) -> Tuple[bool, str]:
        """
        Validate a database field value using a clause in the format:
        db_{db_name}.TableName.FieldName[FilterField1=FilterValue1;FilterField2=FilterValue2][OrderBy=CreateTime]=ExpectedValue
        """
        self.setup_database(db_name)
        if not self.db:
            raise ValueError(f"{self.__class__.__name__}: DB connection not configured.")

        pattern = (
            r'^db_\w+\.(?P<Table>\w+)\.(?P<Field>\w+)\s*\[(?P<Filters>[^\]]+)\]'
            r'(?:\s*\[(?P<OrderBy>[^\]]+)\])?\s*=\s*(?P<ExpectedValue>.+)$'
        )
        match = re.match(pattern, db_clause)
        if not match:
            raise ValueError(f"{self.__class__.__name__}: Invalid format: {db_clause}")

        table_name = match.group('Table')
        field_name = match.group('Field')
        filters = match.group('Filters')
        order_by = match.group('OrderBy')
        expected_value = match.group('ExpectedValue').strip()

        # Build WHERE clause
        where_clause = " AND ".join(
            f"{cond.split('=')[0].strip()} = '{cond.split('=')[1].strip()}'"
            for cond in filters.split(';') if '=' in cond
        )

        order_by_clause = order_by.replace('OrderBy=', '').strip() if order_by else ""
        sql_query = f"SELECT {field_name} FROM {table_name}"
        if where_clause:
            sql_query += f" WHERE {where_clause}"
        if order_by_clause:
            sql_query += f" ORDER BY {order_by_clause}"

        logging.info(f"{self.__class__.__name__}: SQL query: {sql_query}")

        result = self.db.execute_query(table_name, fields=[field_name], where=where_clause, order_by=order_by_clause)
        if not result:
            msg = f"No data found for '{field_name}' in '{table_name}'"
            if where_clause:
                msg += f" with filters: {where_clause}"
            if order_by_clause:
                msg += f" and order: {order_by_clause}"
            raise AssertionError(msg)

        actual_value = result[0][field_name]
        msg = (
            f"Validation for '{field_name}' in '{table_name}': "
            f"Expected '{expected_value}', got '{actual_value}'."
        )
        if actual_value != expected_value:
            return False, msg

        logging.info(
            f"{self.__class__.__name__}: Value matched. {msg} | Executed SQL: {sql_query}"
        )
        return True, msg

    def flexible_insert(self, db_name: str, table: str, data_template: Dict[str, Any], row_count: int = 1) -> int:
        """
        Insert rows into a table. The data_template supports placeholders:
        e.g., {"id": "{{uuid4}}", "created_at": "{{timestamp}}", "username": "${USER_NAME}"}
        """
        self.setup_database(db_name)
        rows = []
        for _ in range(row_count):
            row_data = {
                col: self._replace_placeholders(value) if isinstance(value, str) else value
                for col, value in data_template.items()
            }
            rows.append(row_data)
        inserted_count = self.db.insert(table, rows)
        logging.info(f"{self.__class__.__name__}: Inserted {inserted_count} row(s) into '{table}'.")
        return inserted_count

    def flexible_update(self, db_name: str, table: str, data_template: Dict[str, Any], where_template: str = "") -> bool:
        """
        Update rows in a table using a data template and an optional where clause template.
        """
        self.setup_database(db_name)
        update_values = {
            col: self._replace_placeholders(value) if isinstance(value, str) else value
            for col, value in data_template.items()
        }
        where_clause = self._replace_placeholders(where_template) if where_template else ""
        success = self.db.update(table, update_values, where=where_clause)
        logging.info(
            f"{self.__class__.__name__}: Update on '{table}' with {update_values} "
            f"and where '{where_clause}' returned {success}."
        )
        return success

    def flexible_delete(self, db_name: str, table: str, where_template: str = "") -> int:
        """
        Delete rows from a table using an optional where clause template.
        """
        self.setup_database(db_name)
        where_clause = self._replace_placeholders(where_template) if where_template else ""
        if hasattr(self.db, "delete"):
            deleted_count = self.db.delete(table, where=where_clause)
            logging.info(
                f"{self.__class__.__name__}: Deleted {deleted_count} row(s) from '{table}' with where '{where_clause}'."
            )
            return deleted_count
        raise NotImplementedError(
            f"{self.__class__.__name__}: Delete operation not supported by the underlying DB."
        )

    def _replace_placeholders(self, template, placeholder_cache=None):
        def replace_dynamic_placeholders(text):
            matches = re.findall(r'\{\{\s*[^}]+?\s*\}\}', text)
            for match in matches:
                if match not in placeholder_cache:
                    try:
                        replaced_value = VariableGenerator.generate_dynamic_value(match.strip())
                        placeholder_cache[match] = str(replaced_value)
                        logging.info(
                            f"{self.__class__.__name__}: Replaced dynamic value {match} with '{replaced_value}'."
                        )
                    except Exception as e:
                        placeholder_cache[match] = f"{{{{UNKNOWN_{match}}}}}"
                        logging.error(
                            f"{self.__class__.__name__}: Failed to replace dynamic value {match}: {e}"
                        )
                text = text.replace(f"{{{{{match}}}}}", placeholder_cache[match])
            return text

        def replace_static_placeholders(text):
            matches = re.findall(r'\$\{([^}]+)\}', text)
            for match in matches:
                replaced_value = BuiltIn().get_variable_value(f'${{{match}}}')
                text = text.replace(f"${{{match}}}", str(replaced_value))
                logging.info(
                    f"{self.__class__.__name__}: Replaced {match} with value '{replaced_value}'."
                )
            return text

        if placeholder_cache is None:
            placeholder_cache = {}

        if isinstance(template, str):
            template = replace_dynamic_placeholders(template)
            template = replace_static_placeholders(template)
        elif isinstance(template, dict):
            for key, value in template.items():
                template[key] = self._replace_placeholders(value, placeholder_cache)
        return template
