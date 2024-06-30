import re
from typing import Dict, Any, Union, List
from libraries.common.log_manager import logger



class ResponseComparator:
    def __init__(self):
        pass

    def compare_response_field(self, actual_response: Union[Dict[str, Any], str], expectation: str) -> Dict[str, Any]:
        if expectation:
            try:
                field_path, expected_value = expectation.split('=')
            except ValueError:
                return self.create_error_comparison_result(expectation, "Invalid [Exp Result] format")

            if field_path.startswith("response"):
                expected_value = expected_value.strip().strip('""').strip("''")
                actual_value = self.extract_actual_value(actual_response, field_path)

                if actual_value is None:
                    return self.create_error_comparison_result(field_path, "Field not found")
                return self.create_comparison_result(field_path, actual_value, expected_value)
            return self.create_not_specified_result()
        else:
            return self.create_not_specified_result()

    def get_save_result(self, actual_response: Union[Dict[str, Any], str], field_path: str):
        actual_value = self.extract_actual_value(actual_response, field_path)
        if actual_value is None:
            return self.create_error_comparison_result(field_path, "Field not found")
        else:
            return self.create_save_result(field_path, actual_value)

    def extract_actual_value(self, actual_response: Union[Dict[str, Any], str], field_path: str) -> str:
        def _extract_value(data, parts):
            if not parts:
                return data
            current_part = parts[0]
            if '[' in current_part and ']' in current_part:
                array_part, idx = re.match(r'(.*)\[(\d+)\]', current_part).groups()
                if array_part in data:
                    return _extract_value(array_part[int(idx)], parts[1:])
                else:
                    return None
            else:
                if isinstance(data, dict) and current_part in data:
                    return _extract_value(data[current_part], parts[1:])
                else:
                    return data

        parts = field_path.split('.')

        if isinstance(actual_response, list) and '[' in parts[0] and ']' in parts[0]:
            match = re.match(r'([a-zA-Z_][a-zA-Z0-9_]*)(\[\d+\])?', parts[0])
            array_index = int(match.group(2)[1:-1])
            actual_response = actual_response[array_index]
        try:
            return _extract_value(actual_response, parts[1:])
        except (KeyError, IndexError, TypeError) as e:
            logger.error(f"Error retrieving the value for path '{field_path}': {str(e)}")
            return None

    def create_error_comparison_result(self, field_path: str, error_message: str) -> Dict[str, str]:
        return {
            "field": field_path if field_path else "N/A",
            "actual_value": "N/A",
            "result": "ERROR",
            "error": error_message
        }

    def create_comparison_result(self, field_path: str, actual_value: Any, expected_value: str) -> Dict[str, Any]:
        return {
            "field": field_path,
            "expected_value": expected_value,
            "actual_value": actual_value,
            "result": "PASS" if str(actual_value) == expected_value else "FAIL"
        }

    def create_comparison_result2(self, field_path: str, actual_value: Any, expected_value) -> Dict[str, Any]:
        return {
            "field": field_path,
            "expected_value": expected_value,
            "actual_value": actual_value,
            "result": "PASS" if actual_value == expected_value else "FAIL"
        }

    def create_not_specified_result(self) -> Dict[str, Any]:
        return {
            "field": "Exp Result",
            "actual_value": "N/A",
            "result": "Not specified"
        }

    def create_save_result(self, field_path, actual_value) -> Dict[str, Any]:
        return {
            "field": field_path,
            "actual_value": actual_value
        }
