import json
from typing import Any, Union, Tuple
import pandas as pd
from jsonpath_ng import parse
import xmltodict
from requests import Response
import logging
from robot.libraries.BuiltIn import BuiltIn
from libraries.common.utility_helpers import UtilityHelpers

builtin_lib = BuiltIn()


class APIResponseProcessor:
    def process_response(self, response: Union[str, Response]) -> Tuple[str, str]:

        if isinstance(response, str):
            content = response.strip()
        elif isinstance(response, Response):
            content = response.text.strip()
        else:
            raise ValueError("Unsupported response type. Expected string or Response object.")

        try:
            json.loads(content)
            logging.info(f"Response content is valid JSON: \n{content}")
            return content, 'json'
        except json.JSONDecodeError:
            try:
                content = UtilityHelpers.format_xml(content)
                logging.info(f"Response content is valid XML:\n{content}")
                return content, 'xml'
            except ValueError:
                raise ValueError("Response content is neither valid JSON nor XML.")

    def _get_json_value(self, json_string: str, json_path: str) -> Any:

        parsed_json = json.loads(json_string)
        jsonpath_expr = parse(f'$.{json_path}')
        matches = [match.value for match in jsonpath_expr.find(parsed_json)]
        if matches:
            return matches[0]
        else:
            raise ValueError(f"No match found for JSONPath: {json_path}")


class APIResponseAsserter(APIResponseProcessor):
    def assert_response(self, expected_results: str, actual_response: Union[str, Response]) -> None:

        logging.info(f"Type of actual_response: {type(actual_response)}")
        logging.info(f"Content of actual_response: {actual_response}")

        response_content, response_format = self.process_response(actual_response)
        expected_lines = expected_results.split('\n')
        assertion_errors = []

        for line in expected_lines:
            if line.strip():
                try:
                    self._assert_line(line.strip(), response_content, response_format)
                except AssertionError as e:
                    logging.error(f"Assertion failed: {str(e)}")
                    assertion_errors.append(str(e))

        if assertion_errors:
            raise AssertionError("Assertions failed:\n" + "\n".join(assertion_errors))

    def _assert_line(self, line: str, response_content: str, response_format: str):
        key, expected_value = line.split('=')
        key = key.strip()
        expected_value = expected_value.strip()

        if response_format == 'json':
            actual_value = self._get_json_value(response_content, key)
        elif response_format == 'xml':
            json_content = json.dumps(xmltodict.parse(response_content))
            actual_value = self._get_json_value(json_content, key)
        else:
            raise ValueError("Unsupported response format. Use 'xml' or 'json'.")

        # Convert values to the same type for comparison
        try:
            expected_value = type(actual_value)(expected_value)
        except ValueError:
            pass  # Keep the original type if conversion fails

        logging.info(f"Key: {key}, Expected value: {expected_value}, Actual value: {actual_value}")
        assert actual_value == expected_value, f"Assertion failed for key '{key}'. Expected: {expected_value}, Actual: {actual_value}"


class APIResponseExtractor(APIResponseProcessor):

    def extract_value(self, response: Union[str, Response], test_case) -> Any:

        response_content, response_format = self.process_response(response)
        save_fields = test_case['Save Fields'].splitlines() if pd.notna(test_case['Save Fields']) else []
        for field in save_fields:

            if response_format == 'json':
                value = self._get_json_value(response_content, field)
            elif response_format == 'xml':
                json_content = json.dumps(xmltodict.parse(response_content))
                value = self._get_json_value(json_content, field)
            else:
                raise ValueError("Unsupported response format. Use 'xml' or 'json'.")
            field = f'{test_case["TCID"]}.{field.strip()}'

            builtin_lib.set_suite_variable('${%s}' % field, value)
