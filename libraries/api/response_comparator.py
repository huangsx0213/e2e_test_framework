import json
import re
from typing import Dict, Any, Union
import requests
from libraries.common.log_manager import logger
import xmltodict

from libraries.common.utility_helpers import UtilityHelpers


class ResponseComparator:
    def __init__(self):
        self.format_xml = UtilityHelpers.format_xml
        self.format_json = UtilityHelpers.format_json

    def extract_response_content(self, response: requests.Response, test_step) -> Union[Dict[str, Any], str]:
        try:
            response = response.json()
            logger.debug(f"[TSID:{test_step['TSID']}] Response content: \n{self.format_json(response)}")
            return response
        except json.JSONDecodeError as json_error:
            logger.warning(f"[TSID:{test_step['TSID']}] JSON decode error: {json_error}. Attempting XML parse.")
            try:
                logger.debug(f"[TSID:{test_step['TSID']}] Response content: \n{response.text}")
                return xmltodict.parse(response.text)
            except Exception as xml_error:
                logger.error(f"[TSID:{test_step['TSID']}] XML parse error: {xml_error}. Returning raw response text.")
                return response.text

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

    def validate_expectations(self, test_step: Dict[str, Union[str, Any]], check_tc_ids: set, pre_check_responses: Dict[str, Dict[str, Any]],
                              post_check_responses: Dict[str, Dict[str, Any]], target_response: Dict[str, Any]) -> bool:
        try:
            for expectation in test_step['Exp Result'].splitlines():
                field_path, expected_value = expectation.split('=')
                field_path = field_path.strip()
                expected_value = expected_value.strip()

                if field_path.startswith(tuple(check_tc_ids)):
                    check_tc_id, _ = field_path.split('.', 1)
                    check_tc_id, _ = check_tc_id.split('[', 1)
                    expected_delta = int(expected_value)

                    pre_value = self.extract_actual_value(pre_check_responses[check_tc_id], field_path)
                    post_value = self.extract_actual_value(post_check_responses[check_tc_id], field_path)

                    delta = post_value - pre_value
                    if delta != expected_delta:
                        raise AssertionError(f"Check-with condition failed for {field_path}: {delta} != {expected_delta}")
                else:
                    actual_value = self.extract_actual_value(target_response, field_path)
                    if str(actual_value) != expected_value:
                        logger.error(f"Expectation failed for {field_path}: {actual_value} != {expected_value}")
                        return False
            return True
        except Exception as e:
            logger.error(f"Validation of expectations failed: {str(e)}")
            return False