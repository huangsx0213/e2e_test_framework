import logging
import json
import re
from typing import Any, Union, Tuple

from jsonpath_ng import parse
import xmltodict
from requests import Response
from robot.libraries.BuiltIn import BuiltIn

from libraries.common.utility_helpers import UtilityHelpers

builtin_lib = BuiltIn()


class APIResponseProcessor:
    def process_response(self, response: Union[str, Response]) -> Tuple[str, str]:
        try:
            content = response.text.strip() if isinstance(response, Response) else response.strip()

            if self._is_json(content):
                return content, 'json'
            if self._is_xml(content):
                return UtilityHelpers.format_xml(content), 'xml'

            raise ValueError(f"{self.__class__.__name__}: Response content is neither valid JSON nor XML.")
        except Exception as e:
            logging.error(f"{self.__class__.__name__}: Error processing response: {str(e)}")
            raise

    def _is_json(self, content: str) -> bool:
        try:
            json.loads(content)
            return True
        except json.JSONDecodeError:
            return False

    def _is_xml(self, content: str) -> bool:
        try:
            xmltodict.parse(content)
            return True
        except xmltodict.expat.ExpatError:
            return False

    def _get_json_value(self, json_string: str, json_path: str) -> Any:
        parsed_json = json.loads(json_string)
        jsonpath_expr = parse(f'$.{json_path}')
        matches = [match.value for match in jsonpath_expr.find(parsed_json)]
        if matches:
            return matches[0]
        else:
            raise ValueError(f"{self.__class__.__name__}: No match found for JSONPath: {json_path}")

    def _extract_value_from_response(self, response: Union[str, Response], json_path: str) -> Any:
        response_content, response_format = self.process_response(response)

        if response_format == 'json':
            return self._get_json_value(response_content, json_path)
        elif response_format == 'xml':
            json_content = json.dumps(xmltodict.parse(response_content))
            return self._get_json_value(json_content, json_path)
        else:
            raise ValueError(f"{self.__class__.__name__}: Unsupported response format. Use 'xml' or 'json'.")

    def _compare_diff(self, actual_diff: float, expected_diff: str) -> bool:
        expected_operator = expected_diff[0]
        expected_value = float(expected_diff[1:])

        if expected_operator == '+':
            return actual_diff == expected_value
        elif expected_operator == '-':
            return actual_diff == -expected_value
        else:
            raise ValueError(f"{self.__class__.__name__}: Unsupported operator in expected diff: {expected_operator}")


class APIResponseAsserter(APIResponseProcessor):
    def validate_response(self, expected_results: str, actual_response: Union[str, Response]) -> None:
        response_content, response_format = self.process_response(actual_response)
        logging.info(f"{self.__class__.__name__}: Actual response:\n{response_content}")

        expected_lines = expected_results.splitlines()
        assertion_errors = []

        for line in expected_lines:
            if line.strip().startswith('$'):
                try:
                    self._assert_line(line.strip(), response_content, response_format)
                except AssertionError as e:
                    logging.error(f"{self.__class__.__name__}: Assertion failed: {str(e)}")
                    assertion_errors.append(str(e))

        if assertion_errors:
            raise AssertionError(f"{self.__class__.__name__}: Assertions failed:\n" + "\n".join(assertion_errors))

    def _assert_line(self, line: str, response_content: str, response_format: str) -> None:
        key, expected_value = map(str.strip, line.split('=', 1))

        actual_value = self._extract_value_from_response(response_content, key)

        # Convert values to the same type for comparison
        try:
            expected_value = type(actual_value)(expected_value)
        except (ValueError, TypeError):
            pass  # Keep the original type if conversion fails

        logging.info(f"{self.__class__.__name__}: Asserting: {key}, Expected: {expected_value}, Actual: {actual_value}")
        assert actual_value == expected_value, f"{self.__class__.__name__}: Assertion failed for key '{key}'. Expected: {expected_value}, Actual: {actual_value}"

    def validate_dynamic_checks(self, test_case: dict, pre_check_responses: dict, post_check_responses: dict) -> None:
        exp_results = test_case['Exp Result'].splitlines()
        for exp_result in exp_results:
            dynamic_checks = re.findall(r'(\w+)\.(\$[.\[\]\w]+)=([+-]\d+)', exp_result)
            if dynamic_checks:
                logging.info(f"{self.__class__.__name__}: Expected result: {exp_result}")

            for check in dynamic_checks:
                tcid, json_path, expected_value = check
                pre_value = self._extract_value_from_response(pre_check_responses[tcid], json_path)
                post_value = self._extract_value_from_response(post_check_responses[tcid], json_path)
                actual_value = round(float(post_value) - float(pre_value), 2)

                logging.info(f"{self.__class__.__name__}: Actual diff: {actual_value}, Expected diff: {expected_value}")

                if not self._compare_diff(actual_value, expected_value):
                    raise AssertionError(f"{self.__class__.__name__}: Dynamic check failed for {tcid}.{json_path}. Expected: {expected_value}, Actual: {actual_value}")

                logging.info(f"{self.__class__.__name__}: Dynamic check passed for {tcid}.{json_path}")


class APIResponseExtractor(APIResponseProcessor):
    def extract_value(self, response: Union[str, Response], test_case: dict) -> None:
        response_content, response_format = self.process_response(response)
        save_fields = test_case.get('Save Fields', '').splitlines()

        for field in save_fields:
            try:
                value = self._extract_value_from_response(response_content, field)
                field_name = f'{test_case["TCID"]}.{field.strip()}'
                logging.info(f"{self.__class__.__name__}: Setting suite variable {field_name} to {value}.")
                BuiltIn().set_global_variable(f'${{{field_name}}}', value)
            except Exception as e:
                logging.error(f"{self.__class__.__name__}: Failed to process field '{field}': {e}")
