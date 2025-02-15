import logging
import os
import re
from typing import Tuple, Any, Dict
from libraries.common.db import SQLAlchemyDatabase
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


class DBOperator(metaclass=SingletonMeta):

    def __init__(self):
        if not hasattr(self, '_initialized'):
            self.db_connections: Dict[str, SQLAlchemyDatabase] = {}
            self.db_configs = self._load_db_configs()
            self.active_environment = self._get_active_environment()
            self._initialize_databases()
            self._initialized = True

    def _load_db_configs(self) -> Dict[str, Any]:
        config_path = os.path.join(PROJECT_ROOT, 'configs', 'db_config.yaml')
        return ConfigManager.load_yaml(config_path)

    def _get_active_environment(self) -> str:
        return BuiltIn().get_variable_value("${active_environment}")

    def _initialize_databases(self):
        env_db_configs = self.db_configs.get('database', {}).get(self.active_environment, {})
        self.db_connections = SQLAlchemyDatabase.create_databases(env_db_configs)

    def get_db_connection(self, db_name: str) -> SQLAlchemyDatabase:
        db_conn = self.db_connections.get(db_name)
        if not db_conn:
            raise ValueError(f"Database connection '{db_name}' not found.")
        return db_conn

    # --- 数据验证方法 ---

    def validate_database_value(self, db_name: str, db_clause: str) -> Tuple[bool, str]:
        """
        Validate a database field value using a clause in the format:
        db_{db_name}.TableName.FieldName[FilterField1=FilterValue1;FilterField2=FilterValue2][OrderBy=CreateTime]=ExpectedValue
        """
        db = self.get_db_connection(db_name)
        if not db:
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
                if '=' not in condition:
                    raise ValueError(f"{self.__class__.__name__}: Invalid filter condition: {condition}")
                filter_field, filter_value = condition.split('=', 1)
                where_clauses.append(f"{filter_field.strip()} = '{filter_value.strip()}'")
            where_clause = " AND ".join(where_clauses)

        order_by_clause = f"{order_by.replace('OrderBy=', '').strip()}" if order_by else ""

        sql_query = f"SELECT {field_name} FROM {table_name}"
        if where_clause:
            sql_query += f" WHERE {where_clause}"
        if order_by_clause:
            sql_query += f" ORDER BY {order_by_clause}"

        logging.info(f"{self.__class__.__name__}: Generated SQL query: {sql_query}")

        result = db.execute_query(table_name, fields=[field_name], where=where_clause, order_by=order_by_clause)
        if not result:
            no_data_message = f"No data found for field '{field_name}' in table '{db_name}.{table_name}'."
            if where_clause:
                no_data_message += f" Filter applied: {where_clause}."
            if order_by_clause:
                no_data_message += f" Order: {order_by_clause}."
            raise AssertionError(no_data_message)

        actual_value = result[0][field_name]
        msg = (
            f"Database validation for '{field_name}' in table '{db_name}.{table_name}'. "
            f"Expected: '{expected_value}', Actual: '{actual_value}'."
        )
        if actual_value != expected_value:
            return False, msg

        logging.info(
            f"{self.__class__.__name__}: Database value matched for '{field_name}' in table '{db_name}.{table_name}'. "
            f"Expected: '{expected_value}', Actual: '{actual_value}'. Executed SQL: {sql_query}"
        )
        return True, msg

    # --- 数据操作方法 ---

    def insert_data(self, db_name: str, table: str, data_template: Dict[str, Any], row_count: int = 1) -> int:
        """
        插入一行或多行数据到指定的表中，支持模板中的占位符替换。

        :param db_name: 数据库连接名称。
        :param table: 表名。
        :param data_template: 插入数据的模板字典，支持占位符。
        :param row_count: 要插入的行数。
        :return: 插入的行数。
        """
        db = self.get_db_connection(db_name)
        rows = [
            {col: self._replace_placeholders(value) if isinstance(value, str) else value
             for col, value in data_template.items()}
            for _ in range(row_count)
        ]
        with db.transaction():
            inserted_count = db.insert(table, rows)
            logging.info(f"{self.__class__.__name__}: Inserted {inserted_count} row(s) into '{table}'.")
            return inserted_count

    def update_data(self, db_name: str, table: str, data_template: Dict[str, Any],
                    where_template: str = "") -> bool:
        """
        根据数据模板和可选的 WHERE 子句模板更新表中行。

        :param db_name: 数据库连接名称。
        :param table: 表名。
        :param data_template: 更新数据的模板字典，支持占位符。
        :param where_template: 可选的 WHERE 子句模板，支持占位符。
        :return: 如果更新成功返回 True，否则返回 False。
        """
        db = self.get_db_connection(db_name)
        update_values = {
            col: self._replace_placeholders(value) if isinstance(value, str) else value
            for col, value in data_template.items()
        }
        where_clause = self._replace_placeholders(where_template) if where_template else ""
        with db.transaction():
            success = db.update(table, update_values, where=where_clause)
            logging.info(
                f"{self.__class__.__name__}: Update on '{table}' with {update_values} "
                f"and where '{where_clause}' returned {success}."
            )
            return success

    def delete_data(self, db_name: str, table: str, where_template: str = "") -> int:
        """
        根据可选的 WHERE 子句模板从表中删除行。

        :param db_name: 数据库连接名称。
        :param table: 表名。
        :param where_template: 可选的 WHERE 子句模板，支持占位符。
        :return: 删除的行数。
        """
        db = self.get_db_connection(db_name)
        where_clause = self._replace_placeholders(where_template) if where_template else ""

        with db.transaction():
            deleted_count = db.delete(table, where=where_clause)
            logging.info(
                f"{self.__class__.__name__}: Deleted {deleted_count} row(s) from '{table}' with where '{where_clause}'.")
            return deleted_count

    # --- 工具方法 ---

    def _replace_placeholders(self, template, placeholder_cache=None):
        """
        替换字符串或字典中的占位符为实际值。
        """

        def replace_dynamic_variables(text):
            matches = re.findall(r'\{\{\s*([^}]+?)\s*\}\}', text)
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

        def replace_robot_variables(text):
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
            template = replace_dynamic_variables(template)
            template = replace_robot_variables(template)
        elif isinstance(template, dict):
            for key, value in template.items():
                template[key] = self._replace_placeholders(value, placeholder_cache)
        return template
