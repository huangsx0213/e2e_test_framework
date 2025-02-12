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
    def __init__(self):
        self.db = None
        self.db_name = None
        self.db_cache = {}
        self.db_configs = self._load_db_configs()
        self.active_environment = self._get_active_environment()

    def _load_db_configs(self) -> Dict[str, Any]:
        config_path = os.path.join(PROJECT_ROOT, 'configs', 'db_config.yaml')
        return ConfigManager.load_yaml(config_path)

    def _get_active_environment(self) -> str:
        return BuiltIn().get_variable_value("${active_environment}")

    def setup_database(self, db_name: str) -> None:

        db_config = (
            self.db_configs.get('database', {})
            .get(self.active_environment, {})
            .get(db_name.lower())
        )
        if not db_config:
            raise ValueError(
                f"{self.__class__.__name__}: No database configuration found for prefix: {db_name} in environment: {self.active_environment}"
            )

        db_key = self.get_db_key(db_config)
        if db_key in self.db_cache:
            self.db = self.db_cache[db_key]
            logging.info(f"{self.__class__.__name__}: Using cached DB connection for {db_key}")
        else:
            db_type = db_config.pop('type').lower()
            self.db = create_database(db_type, **db_config)
            self.db_cache[db_key] = self.db
            logging.info(f"{self.__class__.__name__}: New DB connection created and cached for {db_key}")

    def get_db_key(self, db_config: Dict[str, Any]) -> str:
        db_type = db_config['type'].lower()
        host = db_config.get('host', 'localhost')
        port = db_config.get('port', 3306)
        self.db_name = db_config.get('database', '')
        return f"{db_type}_{host}_{port}_{self.db_name}"

    def validate_database_value(self, db_clause: str) -> Tuple[bool, str]:
        """
          db_{db_name}.TableName.FieldName[FilterField1=FilterValue1;FilterField2=FilterValue2][OrderBy=CreateTime]=ExpectedValue
        """
        if not self.db:
            raise ValueError(f"{self.__class__.__name__}: Database connection is not configured.")

        pattern = (
            r'^db_\w+\.(?P<Table>\w+)\.(?P<Field>\w+)\s*\[(?P<Filters>[^\]]+)\]'
            r'(?:\s*\[(?P<OrderBy>[^\]]+)\])?\s*=\s*(?P<ExpectedValue>.+)$'
        )
        match = re.match(pattern, db_clause)
        if not match:
            raise ValueError(f"{self.__class__.__name__}: Invalid format for validate_database_value: {db_clause}")

        table_name = match.group('Table')
        field_name = match.group('Field')
        filters = match.group('Filters')
        order_by = match.group('OrderBy')
        expected_value = match.group('ExpectedValue').strip()

        # 构建 WHERE 子句
        where_clause = ""
        if filters:
            filter_conditions = filters.split(';')
            where_clauses = []
            for condition in filter_conditions:
                filter_field, filter_value = condition.split('=')
                where_clauses.append(f"{filter_field} = '{filter_value}'")
            where_clause = " AND ".join(where_clauses)

        order_by_clause = f"{order_by.replace('OrderBy=', '')}" if order_by else ""

        sql_query = f"SELECT {field_name} FROM {table_name}"
        if where_clause:
            sql_query += f" WHERE {where_clause}"
        if order_by_clause:
            sql_query += f" ORDER BY {order_by_clause}"

        logging.info(f"{self.__class__.__name__}: Generated SQL query: {sql_query}")

        result = self.db.execute_query(table_name, fields=[field_name], where=where_clause, order_by=order_by_clause)
        if not result:
            no_data_message = f"No data found for field '{field_name}' in table '{table_name}'."
            if where_clause:
                no_data_message += f" Filter applied: {where_clause}."
            if order_by_clause:
                no_data_message += f" Order: {order_by_clause}."
            raise AssertionError(no_data_message)

        actual_value = result[0][field_name]
        msg = (
            f"Database validation for '{field_name}' in table '{self.db_name}.{table_name}'. "
            f"Expected: '{expected_value}', Actual: '{actual_value}'."
        )
        if actual_value != expected_value:
            return False, msg

        logging.info(
            f"{self.__class__.__name__}: Database value matched for '{field_name}' in table '{self.db_name}.{table_name}'. "
            f"Expected: '{expected_value}', Actual: '{actual_value}'. Executed SQL: {sql_query}"
        )
        return True, msg

    def _replace_placeholders(self, template_str: str) -> str:
        builtin = BuiltIn()

        def replace_robot_var(match):
            var_name = match.group(1)
            return str(builtin.get_variable_value('${' + var_name + '}', default=""))

        result = re.sub(r'\$\{([^}]+)\}', replace_robot_var, template_str)

        def replace_dynamic(match):
            dynamic_field = match.group(1).strip()
            try:
                return str(VariableGenerator.generate_dynamic_value(dynamic_field))
            except Exception as e:
                return f"{{{{UNKNOWN_{dynamic_field}}}}}"

        result = re.sub(r'\{\{\s*([^}]+?)\s*\}\}', replace_dynamic, result)
        return result

    def flexible_insert(self, table: str, data_template: Dict[str, Any], row_count: int = 1) -> int:
        """
        data_template: {"id": "{{uuid4}}", "created_at": "{{timestamp}}", "username": "${USER_NAME}"}
        """
        rows = []
        for _ in range(row_count):
            row_data = {}
            for col, value in data_template.items():
                if isinstance(value, str):
                    row_data[col] = self._replace_placeholders(value)
                else:
                    row_data[col] = value
            rows.append(row_data)
        inserted_count = self.db.insert(table, rows)
        logging.info(f"{self.__class__.__name__}: Inserted {inserted_count} rows into table '{table}'.")
        return inserted_count

    def flexible_update(self, table: str, data_template: Dict[str, Any], where_template: str = "") -> bool:
        update_values = {}
        for col, value in data_template.items():
            if isinstance(value, str):
                update_values[col] = self._replace_placeholders(value)
            else:
                update_values[col] = value

        where_clause = self._replace_placeholders(where_template) if where_template else ""
        success = self.db.update(table, update_values, where=where_clause)
        logging.info(
            f"{self.__class__.__name__}: Update on table '{table}' with values {update_values} and where clause '{where_clause}' returned {success}."
        )
        return success

    def flexible_delete(self, table: str, where_template: str = "") -> int:
        where_clause = self._replace_placeholders(where_template) if where_template else ""
        if hasattr(self.db, "delete"):
            deleted_count = self.db.delete(table, where=where_clause)
            logging.info(
                f"{self.__class__.__name__}: Deleted {deleted_count} rows from table '{table}' with where clause '{where_clause}'."
            )
            return deleted_count
        else:
            raise NotImplementedError(f"{self.__class__.__name__}: Underlying database does not support delete operation.")
