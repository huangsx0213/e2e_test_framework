import logging
import re
import os
from typing import Tuple, Any, Dict
from libraries.common.db import create_database
from robot.libraries.BuiltIn import BuiltIn
from libraries.common.config_manager import ConfigManager
from libraries.common.utility_helpers import PROJECT_ROOT
from libraries.common.variable_generator import VariableGenerator


class DBOperator:
    """
    A database operator that handles connection caching and common operations
    like validation, insertion, update, and deletion.
    """

    def __init__(self):
        self.db = None
        self.db_cache = {}
        self.db_configs = self._load_db_configs()
        self.active_environment = self._get_active_environment()

    def _load_db_configs(self) -> Dict[str, Any]:
        """Load database configurations from a YAML file."""
        config_path = os.path.join(PROJECT_ROOT, 'configs', 'db_config.yaml')
        return ConfigManager.load_yaml(config_path)

    def _get_active_environment(self) -> str:
        """Retrieve the active environment variable from Robot Framework."""
        return BuiltIn().get_variable_value("${active_environment}")

    def setup_database(self, db_name: str) -> None:
        """
        Setup the database connection using the configuration for the given db_name.
        Caches the connection for future use.
        """
        db_config = (
            self.db_configs.get('database', {})
            .get(self.active_environment, {})
            .get(db_name.lower())
        )
        if not db_config:
            raise ValueError(
                f"{self.__class__.__name__}: No config found for db '{db_name}' in environment '{self.active_environment}'."
            )

        db_key = self.get_db_key(db_config)
        if db_key in self.db_cache:
            self.db = self.db_cache[db_key]
            logging.info(f"{self.__class__.__name__}: Using cached connection for {db_key}.")
        else:
            db_type = db_config.pop('type').lower()
            self.db = create_database(db_type, **db_config)
            self.db_cache[db_key] = self.db
            logging.info(f"{self.__class__.__name__}: New connection created and cached for {db_key}.")

    def get_db_key(self, db_config: Dict[str, Any]) -> str:
        """
        Create a unique key for the DB connection based on type, host, port, and database name.
        """
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

        logging.info(f"{self.__class__.__name__}: Value matched. {msg} | Executed SQL: {sql_query}")
        return True, msg

    def _replace_placeholders(self, template_str: str) -> str:
        """
        Replace placeholders in the string:
         - ${VAR_NAME} with Robot Framework variable values.
         - {{ dynamic_expression }} with dynamically generated values.
        """
        builtin = BuiltIn()

        def replace_robot_var(match):
            var_name = match.group(1)
            return str(builtin.get_variable_value('${' + var_name + '}', default=""))

        # Replace Robot Framework variables
        result = re.sub(r'\$\{([^}]+)\}', replace_robot_var, template_str)

        def replace_dynamic(match):
            dynamic_field = match.group(1).strip()
            try:
                return str(VariableGenerator.generate_dynamic_value(dynamic_field))
            except Exception:
                return f"{{{{UNKNOWN_{dynamic_field}}}}}"

        # Replace dynamic values
        return re.sub(r'\{\{\s*([^}]+?)\s*\}\}', replace_dynamic, result)

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
            f"{self.__class__.__name__}: Update on '{table}' with {update_values} and where '{where_clause}' returned {success}."
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
        raise NotImplementedError(f"{self.__class__.__name__}: Delete operation not supported by the underlying DB.")
