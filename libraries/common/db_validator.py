import logging
import re
from libraries.common.db import create_database
from robot.libraries.BuiltIn import BuiltIn

builtin_lib = BuiltIn()


class DBValidator:
    def __init__(self):
        self.db = None
        self.db_name = None
        self.db_cache = {}

    def setup_database(self, db_name: str, db_configs: dict) -> None:
        db_config = db_configs.get(db_name.lower())
        if not db_config:
            raise ValueError(f"{self.__class__.__name__}: No database configuration found for prefix: {db_name}")

        db_key = self.get_db_key(db_config)
        if db_key in self.db_cache:
            self.db = self.db_cache[db_key]
            logging.info(f"{self.__class__.__name__}: Using cached DB connection for {db_key}")
        else:
            db_type = db_config.pop('type').lower()
            self.db = create_database(db_type, **db_config)
            self.db_cache[db_key] = self.db
            logging.info(f"{self.__class__.__name__}: New DB connection created and cached for {db_key}")

    def get_db_key(self, db_config):
        db_type = db_config['type'].lower()
        host = db_config.get('host', 'localhost')
        port = db_config.get('port', 3306)
        self.db_name = db_config.get('database', '')
        return f"{db_type}_{host}_{port}_{self.db_name}"

    def validate_database_value(self, db_clause):
        if not self.db:
            raise ValueError("{self.__class__.__name__}: Database connection is not configured.")

        # Parse the format: db_name1.TableName.FieldName[FilterFieldName=FilterValue;AnotherField=AnotherValue][OrderBy=CreateTime]=ExpectedValue
        pattern = r'^db_\w+\.(?P<Table>\w+)\.(?P<Field>\w+)\s*\[(?P<Filters>[^\]]+)\](?:\s*\[(?P<OrderBy>[^\]]+)\])?\s*=\s*(?P<ExpectedValue>.+)$'

        match = re.match(pattern, db_clause)
        if not match:
            raise ValueError(f"{self.__class__.__name__}: Invalid format for validate_database_value: {db_clause}")

        # Extract components using named groups
        table_name = match.group('Table')
        field_name = match.group('Field')
        filters = match.group('Filters')
        order_by = match.group('OrderBy')
        expected_value = match.group('ExpectedValue').strip()

        # Process filters to build WHERE clause
        where_clause = ''
        if filters:
            filter_conditions = filters.split(';')
            where_clauses = []
            for condition in filter_conditions:
                filter_field, filter_value = condition.split('=')
                where_clauses.append(f"{filter_field} = '{filter_value}'")
            where_clause = ' AND '.join(where_clauses)

        # Process order_by
        if order_by:
            order_by_clause = f"{order_by.replace('OrderBy=', '')}"
        else:
            order_by_clause = ''

        # Build SQL for logging
        sql_query = f"SELECT {field_name} FROM {table_name}"
        if where_clause:
            sql_query += f" WHERE {where_clause}"
        if order_by_clause:
            sql_query += f" ORDER BY {order_by_clause}"

        # Log the generated SQL query
        logging.info(f"{self.__class__.__name__}: Generated SQL query: {sql_query}")

        # Execute the generated query
        result = self.db.execute_query(table_name, fields=[field_name], where=where_clause, order_by=order_by_clause)

        # Validate query result
        if not result:
            no_data_message = f"No data found for field '{field_name}' in table '{table_name}'."
            if where_clause:
                no_data_message += f" Filter applied: {where_clause}."
            if order_by_clause:
                no_data_message += f" Order: {order_by_clause}."
            raise AssertionError(no_data_message)

        actual_value = result[0][field_name]
        msg = f"Database validation for '{field_name}' in table '{self.db_name}.{table_name}'. Expected: '{expected_value}', Actual: '{actual_value}'."
        if actual_value != expected_value:
            return False, msg

        logging.info(
            f"{self.__class__.__name__}: Database value matched for '{field_name}' in table '{self.db_name}.{table_name}'. "
            f"Expected: '{expected_value}', Actual: '{actual_value}'. Executed SQL: {sql_query}"
        )

        return True, msg
