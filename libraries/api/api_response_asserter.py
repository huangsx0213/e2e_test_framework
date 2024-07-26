import logging
from robot.libraries.BuiltIn import BuiltIn
from typing import Any, Union, Tuple
import json
from xml.etree import ElementTree as ET
from requests import Response
from jsonpath_ng import parse
from lxml import etree
from libraries.common.utility_helpers import UtilityHelpers


class APIResponseAsserter:
    def __init__(self):
        self.builtin = BuiltIn()

    def assert_response(self, expected_results: str, actual_response: Union[str, Response]) -> None:
        """
        Assert the actual response against the expected results using Robot Framework's built-in keywords.
        :param expected_results: String containing expected results in the format from Excel
        :param actual_response: Actual response string or Response object
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
                    raise AssertionError("Assertions failed:\n" + "\n".join({str(e)}))


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
            actual_value = self._get_xml_value(response_content, key)
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

    def _get_xml_value(self, xml_string: str, xpath: str) -> str:
        """
        Get value from XML string using lxml for XPath support.
        :param xml_string: XML response as a string
        :param xpath: XPath to the desired element
        :return: Text content of the specified XML element
        """
        xml_tree = etree.fromstring(xml_string)
        result = xml_tree.xpath(xpath)
        if result:
            return result[0].text
        else:
            raise ValueError(f"No match found for XPath: {xpath}")