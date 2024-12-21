import logging
import re
from libraries.common.db import create_database
from robot.libraries.BuiltIn import BuiltIn

builtin_lib = BuiltIn()


class DBValidator:
    def __init__(self):
        self.db = None

    def setup_database(self, db_config):
        db_type = db_config['type'].lower()
        db_config.pop('type')
        self.db = create_database(db_type, **db_config)

    def validate_database_value(self, db_clause):
        if not self.db:
            raise ValueError("Database connection is not configured.")

        # Parse the format DB.TableName.FieldName[FilterFieldName=FilterValue;AnotherField=AnotherValue]=ExpectedValue
        pattern = r'^DB\.(?P<Table>\w+)\.(?P<Field>\w+)\s*\[(?P<Filters>[^\]]+)\]\s*=\s*(?P<ExpectedValue>.+)$'

        match = re.match(pattern, db_clause)
        if not match:
            raise ValueError(f"Invalid format for validate_database_value: {db_clause}")

        # Extract components using named groups
        table_name = match.group('Table')
        field_name = match.group('Field')
        filters = match.group('Filters')
        expected_value = match.group('ExpectedValue').strip()

        # Check if there's a filter part and process it
        if filters:
            filter_conditions = filters.split(';')
            where_clauses = []
            for condition in filter_conditions:
                filter_field, filter_value = condition.split('=')
                where_clauses.append(f"{filter_field} = '{filter_value}'")
            where_clause = ' AND '.join(where_clauses)
        else:
            where_clause = None

        # Query the database
        result = self.db.execute_query(table_name, fields=[field_name], where=where_clause)

        if not result:
            if where_clause:
                raise AssertionError(f"No data found for {field_name} in {table_name} where {where_clause}")
            else:
                raise AssertionError(f"No data found for {field_name} in {table_name}")

        actual_value = result[0][field_name]

        if actual_value != expected_value:
            raise AssertionError(f"Database value mismatch. Expected {expected_value} but got {actual_value} for {field_name} in {table_name}")

        logging.info(f"{self.__class__.__name__}: Database value matched for {field_name} in {table_name}. Expected: {expected_value}, Actual: {actual_value}")
        logging.info(f"{self.__class__.__name__}: {db_clause} passed.")


