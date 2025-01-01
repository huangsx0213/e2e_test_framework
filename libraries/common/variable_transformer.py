import re
import datetime
from robot.libraries.BuiltIn import BuiltIn
from typing import Any, Dict
from robot.api import logger
from libraries.common.log_manager import ColorLogger
from libraries.common.variable_generator import VariableGenerator


class VariableTransformer:
    def __init__(self):
        self.builtin = BuiltIn()
        self.functions = {
            'to_iso_date': self._to_iso_date,
            'to_timestamp': self._to_timestamp,
            'to_upper': self._to_upper,
            'to_lower': self._to_lower,
            'remove_spaces': self._remove_spaces,
            'extract_numbers': self._extract_numbers,
            'add': self._add,
            'subtract': self._subtract,
            'multiply': self._multiply,
            'divide': self._divide,
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

    # Function definitions
    def _to_iso_date(self, value: str) -> str:
        date_obj = datetime.datetime.strptime(value, "%Y%m%d")
        return date_obj.strftime("%Y-%m-%d")

    def _to_timestamp(self, value: str) -> int:
        date_obj = datetime.datetime.strptime(value, "%Y-%m-%d")
        return int(date_obj.timestamp())

    def _to_upper(self, value: str) -> str:
        return value.upper()

    def _to_lower(self, value: str) -> str:
        return value.lower()

    def _remove_spaces(self, value: str) -> str:
        return value.replace(" ", "")

    def _extract_numbers(self, value: str) -> str:
        return ''.join(filter(str.isdigit, value))

    def _add(self, value: str) -> float:
        numbers = [float(n) for n in value.split(',')]
        return sum(numbers)

    def _subtract(self, value: str) -> float:
        numbers = [float(n) for n in value.split(',')]
        return numbers[0] - sum(numbers[1:])

    def _multiply(self, value: str) -> float:
        numbers = [float(n) for n in value.split(',')]
        result = 1
        for n in numbers:
            result *= n
        return result

    def _divide(self, value: str) -> float:
        numbers = [float(n) for n in value.split(',')]
        return numbers[0] / numbers[1] if numbers[1] != 0 else float('inf')
