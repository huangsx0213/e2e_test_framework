import logging
from robot.libraries.BuiltIn import BuiltIn
from typing import Any, Union, Tuple
import json
from xml.etree import ElementTree as ET
from requests import Response
from jsonpath_ng import parse
from lxml import etree
import yaml
import xmltodict
from libraries.common.utility_helpers import UtilityHelpers


class APIResponseAsserter:
    def __init__(self):
        self.builtin = BuiltIn()

    def assert_response(self, expected_results: str, actual_response: Union[str, Response], save_fields: str = None, yaml_file_path: str = None, tcid: str = None) -> None:
        """
        Assert the actual response against the expected results using Robot Framework's built-in keywords.
        Optionally save specified fields into a YAML file with tcid as prefix.
        :param expected_results: String containing expected results in the format from Excel
        :param actual_response: Actual response string or Response object
        :param save_fields: Fields to be saved (optional)
        :param yaml_file_path: Path to the YAML file where fields should be saved (optional)
        :param tcid: Test case identifier to prefix the saved fields (optional)
        :raises AssertionError: If any assertion fails
        """
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

        if save_fields and yaml_file_path and tcid:
            self.save_fields_to_yaml(save_fields, response_content, response_format, yaml_file_path, tcid)

    def process_response(self, response: Union[str, Response]) -> Tuple[str, str]:
        """
        Process the response and detect its format.
        :param response: Response string or Response object
        :return: Tuple of (response content, detected format)
        """
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
                ET.fromstring(content)
                logging.info(f"Response content is valid XML: \n{UtilityHelpers.format_xml(content)}")
                return content, 'xml'
            except ET.ParseError:
                raise ValueError("Unable to detect response format. The response is neither valid JSON nor valid XML.")

    def _assert_line(self, line: str, response_content: str, response_format: str):
        """
        Assert a single line of expected result against the response using Robot Framework's built-in keywords.
        :param line: Single line of expected result
        :param actual_response: Actual response string (XML or JSON)
        :param response_format: Format of the response ('xml' or 'json')
        """
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
        # Use Robot Framework's built-in keyword for assertion
        self.builtin.should_be_equal(actual_value, expected_value,
                                     msg=f"Assertion failed for key '{key}'. Expected: {expected_value}, Actual: {actual_value}")

    def _get_json_value(self, json_string: str, json_path: str) -> Any:
        """
        Get value from JSON string using jsonpath-ng.
        :param json_string: JSON response as a string
        :param json_path: JSONPath to the desired value
        :return: Value at the specified JSONPath
        """
        parsed_json = json.loads(json_string)
        jsonpath_expr = parse(f'$.{json_path}')
        matches = [match.value for match in jsonpath_expr.find(parsed_json)]
        if matches:
            return matches[0]
        else:
            raise ValueError(f"No match found for JSONPath: {json_path}")

    def save_fields_to_yaml(self, save_fields: str, response_content: str, response_format: str, yaml_file_path: str, tcid: str):
        """
        Save specified fields from the response to a YAML file.
        :param save_fields: Fields to be saved, separated by commas
        :param response_content: Response content as a string
        :param response_format: Format of the response ('json' or 'xml')
        :param yaml_file_path: Path to the YAML file where fields should be saved
        :param tcid: Test case identifier to prefix the saved fields
        """
        fields = [field.strip() for field in save_fields.split(',')]
        data_to_save = {}

        if response_format == 'xml':
            response_content = json.dumps(xmltodict.parse(response_content))

        for field in fields:
            value = self._get_json_value(response_content, field)
            data_to_save[f"{tcid}.{field}"] = value

        with open(yaml_file_path, 'w') as yaml_file:
            yaml.dump(data_to_save, yaml_file, default_flow_style=False)
        logging.info(f"Saved fields to YAML file at {yaml_file_path}")