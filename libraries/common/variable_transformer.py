import re
import datetime

import pytz
from robot.libraries.BuiltIn import BuiltIn
from typing import Any, Dict
from robot.api import logger
from libraries.common.log_manager import ColorLogger
from libraries.common.variable_generator import VariableGenerator


class VariableTransformer:
    def __init__(self):
        self.builtin = BuiltIn()
        self.functions = {
            'to_iso_date': self._compact_to_iso_date,
            'to_compact_date': self._iso_to_compact_date,
            'utc_to_poland_iso_datetime': self._utc_to_poland_iso_datetime,
            'to_uppercase': lambda x: x.upper(),
            'to_lowercase': lambda x: x.lower(),
            'assign_value': lambda x: x,
        }

    def transform(self, transformations, test_case: Dict[str, Any]) -> None:
        for function_name, input_field, output_field in transformations:
            if output_field is None:
                output_field = self._get_output_field(input_field)
            input_value = self._get_input_value(input_field, test_case)

            if function_name not in self.functions:
                raise ValueError(f"Unknown function: {function_name}")

            output_value = self.functions[function_name](input_value)

            self._save_as_global_variable(output_field, output_value)

    def _get_input_value(self, input_field: str, test_case: Dict[str, Any]) -> Any:
        if input_field.startswith('{{') and input_field.endswith('}}'):
            # Generate dynamic value
            dynamic_field = re.findall(r'{{(.*?)}}', input_field)[0]
            return VariableGenerator.generate_dynamic_value(dynamic_field)
        elif input_field.startswith('${') and input_field.endswith('}'):
            # Get Robot Framework variable
            return self.builtin.get_variable_value(input_field)
        elif input_field in test_case:
            # Get value from test case
            return test_case[input_field]
        else:
            # Try to get it as a global variable
            return self.builtin.get_variable_value(f"${{{input_field}}}")

    def _get_output_field(self, input_field: str) -> Any:
        if input_field.startswith('{{') and input_field.endswith('}}'):
            dynamic_field = re.findall(r'{{(.*?)}}', input_field)[0]
            return dynamic_field
        elif input_field.startswith('${') and input_field.endswith('}'):
            field_name = re.findall(r'\$\{\s*(.*?)\s*\}', input_field)[0]
            return field_name

    def _save_as_global_variable(self, output_field: str, value: Any) -> None:
        logger.info(ColorLogger.info(f"=> {self.__class__.__name__}: Setting global variable ${{{output_field}}} to {value}."), html=True)
        self.builtin.set_global_variable(f'${{{output_field}}}', value)

    # e.g. 20230101 -> 2023-01-01
    def _compact_to_iso_date(self, value: str) -> str:
        date_obj = datetime.datetime.strptime(value, "%Y%m%d")
        return date_obj.strftime("%Y-%m-%d")

    # e.g. 2023-01-01 -> 20230101
    def _iso_to_compact_date(self, value: str) -> str:
        date_obj = datetime.datetime.strptime(value, "%Y-%m-%d")
        return date_obj.strftime("%Y%m%d")

    # e.g. 2023-10-05T12:00:00.000Z -> 2023-10-05T14:00:00+02:00
    def _utc_to_poland_iso_datetime(self, utc_datetime_str: str) -> str:
        utc_datetime = datetime.datetime.strptime(utc_datetime_str, "%Y-%m-%dT%H:%M:%S.%fZ").replace(microsecond=0)
        poland_zone = pytz.timezone('Europe/Warsaw')
        poland_datetime = utc_datetime.astimezone(poland_zone)
        return poland_datetime.isoformat()


if __name__ == "__main__":
    vt = VariableTransformer()
    print(vt._compact_to_iso_date("20230101"))
    print(vt._iso_to_compact_date("2023-01-01"))
    print(vt._utc_to_poland_iso_datetime("2023-10-05T12:00:00.000Z"))
