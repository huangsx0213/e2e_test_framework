import json
import re
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
            logging.info(f"Response content is valid JSON string.")
            return content, 'json'
        except json.JSONDecodeError:
            try:
                content = UtilityHelpers.format_xml(content)
                logging.info(f"Response content is valid XML string.")
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
    def _extract_value_from_response(self, response, json_path):
        json_data = json.loads(response.text)
        jsonpath_expr = parse(f'$.{json_path}')
        matches = [match.value for match in jsonpath_expr.find(json_data)]
        if matches:
            return float(matches[0])
        raise ValueError(f"No match found for JSONPath: {json_path}")
    def _compare_diff(self, actual_diff, expected_diff):
        expected_operator = expected_diff[0]
        expected_value = float(expected_diff[1:])

        if expected_operator == '+':
            return actual_diff == expected_value
        elif expected_operator == '-':
            return actual_diff == -expected_value
        else:
            raise ValueError(f"Unsupported operator in expected diff: {expected_operator}")
class APIResponseAsserter(APIResponseProcessor):
    def validate_response(self, expected_results: str, actual_response: Union[str, Response]) -> None:

        logging.info(f"Expected results:\n{expected_results}")
        response_content, response_format = self.process_response(actual_response)
        logging.info(f"Actual response:\n{response_content}")

        expected_lines = expected_results.split('\n')
        assertion_errors = []

        for line in expected_lines:
            if line.strip():
                if line.strip().startswith('$'):
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

        logging.info(f"Asserting for: {key}, Expected value: {expected_value}, Actual value: {actual_value}")
        assert actual_value == expected_value, f"Assertion failed for key '{key}'. Expected: {expected_value}, Actual: {actual_value}"

    def validate_dynamic_checks(self, test_case, pre_check_responses, post_check_responses):
        exp_results = test_case['Exp Result'].split('\n')
        for exp_result in exp_results:
            dynamic_checks = re.findall(r'(\w+)\.([^=]+)=([+-]?\d+(?:\.\d+)?)', exp_result)
            if dynamic_checks:
                logging.info(f"Expected result: {exp_result}")

            for check in dynamic_checks:
                tcid, json_path, expected_value = check
                if not tcid.startswith('$'):  # Only process checks that don't start with '$'
                    # This is a dynamic check involving other test cases
                    pre_value = self._extract_value_from_response(pre_check_responses[tcid], json_path)
                    logging.info(f"Pre check value:{tcid}.{json_path}= {pre_value}")
                    post_value = self._extract_value_from_response(post_check_responses[tcid], json_path)
                    logging.info(f"Post check value:{tcid}.{json_path}= {post_value}")
                    actual_value = post_value - pre_value
                    logging.info(f"Actual value: Post check value - Pre check value = {'+' if actual_value >= 0 else '-'}{actual_value}.")


                    if not self._compare_diff(actual_value, expected_value):
                        raise AssertionError(f"Dynamic check failed for {tcid}.{json_path}. "
                                             f"Expected: {expected_value}, Actual: {'+' if actual_value >= 0 else '-'}{actual_value}.")
                    logging.info(f"****** Dynamic check passed for {tcid}.{json_path} ******")
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

            logging.info(f"Setting suite variable:")
            builtin_lib.set_suite_variable(f'${{{field}}}', value)




