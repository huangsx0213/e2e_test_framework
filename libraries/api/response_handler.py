import logging
import json
import re
from typing import Any, Union, Tuple, List, Dict
from jsonpath_ng import parse
import xmltodict
from requests import Response
from robot.libraries.BuiltIn import BuiltIn
from robot.api import logger
from libraries.db.db_operator import DBOperator
from libraries.common.log_manager import ColorLogger
from libraries.common.utility_helpers import UtilityHelpers
from libraries.common.variable_transformer import VariableTransformer

builtin_lib = BuiltIn()


class ResponseHandler:
    def get_content_and_format(self, response: Union[str, Response]) -> Tuple[str, str]:
        try:
            content = self._get_raw_content(response)
            response_format = self._determine_format(content)
            if response_format == 'xml':
                content = UtilityHelpers.format_xml(content)
            return content, response_format
        except Exception as e:
            msg = f"{self.__class__.__name__}: Error processing response: {e}"
            logging.error(msg)
            raise ValueError(msg) from e

    def _get_raw_content(self, response: Union[str, Response]) -> str:
        if isinstance(response, Response):
            return response.text.strip()
        elif isinstance(response, str):
            return response.strip()
        else:
            raise TypeError(f"{self.__class__.__name__}: Response must be a requests.Response object or a string.")

    def _determine_format(self, content: str) -> str:
        if self._is_json(content):
            return 'json'
        elif self._is_xml(content):
            return 'xml'
        else:
            raise ValueError(f"{self.__class__.__name__}: Response content is neither valid JSON nor XML.")

    def _extract_value_from_response(self, response: Union[str, Response], json_path: str) -> Any:
        content, response_format = self.get_content_and_format(response)
        return self._extract_value(content, json_path, response_format)

    def _extract_value(self, content: str, json_path: str, response_format: str) -> Any:
        try:
            if response_format == 'xml':
                content = json.dumps(xmltodict.parse(content))

            jsonpath_expr = parse(f'$.{json_path}')
            matches = [match.value for match in jsonpath_expr.find(json.loads(content))]

            if not matches:
                raise ValueError(f"{self.__class__.__name__}: No match found for JSONPath: {json_path}")

            return matches[0]
        except Exception as e:
            msg = f"{self.__class__.__name__}: Error extracting value with JSONPath '{json_path}': {e}"
            logging.error(msg)
            raise ValueError(msg) from e

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
        except Exception:
            return False


class ResponseValidator(ResponseHandler):
    def __init__(self, db_configs):
        super().__init__()
        self.db_configs = db_configs
        self.db_validator = DBOperator()
        self.is_main_test = False

    def validate(self, test_case: dict, response, pre_check_responses=None, post_check_responses=None) -> None:
        logging.info(f"{self.__class__.__name__}: Validating response for test case: {test_case['TCID']}")
        self.is_main_test = test_case['Run'].strip() == 'Y'
        response_content, response_format = self.get_content_and_format(response)
        logging.info(f"{self.__class__.__name__}: Actual response:\n{response_content}")

        current_test_results = self._process_expected_results(test_case, response, pre_check_responses, post_check_responses)

        if current_test_results and any(result['Result'] == 'Fail' for result in current_test_results):
            raise AssertionError(f"{self.__class__.__name__}: Results validation failed for test case: {test_case['TCID']}")

        logging.info(f"{self.__class__.__name__}: All checks passed successfully.")

    def _process_expected_results(self, test_case, response, pre_check_responses, post_check_responses):
        """Processes expected results from the test case."""
        exp_results = test_case['Exp Result'].splitlines()
        current_test_results = []
        for exp_result in exp_results:
            current_test_results.extend(
                self._process_single_expected_result(exp_result, response, pre_check_responses, post_check_responses))
        return current_test_results

    def _process_single_expected_result(self, exp_result, response, pre_check_responses, post_check_responses):
        """Processes a single expected result line."""
        dynamic_checks = re.findall(r'(\w+)\.(?!precheck|postcheck)(\$[.\[\]\w]+)=([+-]\d*\.?\d+)', exp_result)
        pre_post_checks = re.findall(r'(\w+)\.(precheck|postcheck)\.(\$[.\[\]\w]+)=(.+)', exp_result)
        results = []
        if dynamic_checks:
            results.extend(self._handle_dynamic_checks(dynamic_checks, pre_check_responses, post_check_responses))
        elif pre_post_checks:
            results.extend(self._handle_pre_post_checks(pre_post_checks, pre_check_responses, post_check_responses))
        elif exp_result.strip().startswith('$'):
            result = self._handle_response_checks(exp_result.strip(), response)
            results.append(result)
        elif exp_result.strip().startswith('db_'):  # Use 'db_' as prefix
            result = self._handle_db_checks(exp_result.strip())
            results.append(result)
        return results

    def _handle_dynamic_checks(self, checks, pre_check_responses, post_check_responses) -> List[Dict]:
        """Handles dynamic checks (e.g., TC01.$result.total=+1)."""
        results = []
        for tcid, json_path, expected_diff in checks:
            pre_value = self._extract_value_from_response(pre_check_responses[tcid], json_path)
            post_value = self._extract_value_from_response(post_check_responses[tcid], json_path)

            # Format actual_diff to include "+" sign for positive values
            actual_diff_value = round(float(post_value) - float(pre_value), 2)
            actual_diff_str = f"{actual_diff_value:+g}"

            # Format expected_diff to include "+" sign for positive values
            expected_diff_val = round(float(expected_diff), 2)
            expected_diff_str = f"{expected_diff_val:+g}"

            success = actual_diff_value == expected_diff_val
            log_msg = f"Dynamic check for {tcid}.{json_path}. Pre Value: {pre_value}, Post Value:{post_value}, Expected diff: {expected_diff_str}, Actual diff: {actual_diff_str}"
            self._log_result(success, log_msg)

            results.append({"Result": "Pass" if success else "Fail"})
        return results

    def _handle_pre_post_checks(self, checks, pre_check_responses, post_check_responses) -> List[Dict]:
        """Handles pre/post checks (e.g., TC01.precheck.$result.status=success)."""
        results = []
        for tcid, check_type, json_path, expected_value in checks:
            responses = pre_check_responses if check_type == 'precheck' else post_check_responses
            actual_value = self._extract_value_from_response(responses[tcid], json_path)
            expected_value = expected_value.strip()
            success = str(actual_value) == str(expected_value)
            log_msg = f"{check_type.capitalize()} for {tcid}.{json_path} - Expected value: {expected_value}, Actual value: {actual_value}"

            results.append({"Result": "Pass" if success else "Fail"})
            self._log_result(success, log_msg)
        return results

    def _handle_response_checks(self, line: str, response_content: str) -> Dict:
        """Handles direct response checks (e.g., $result.status=success)."""
        key, expected_value = map(str.strip, line.split('=', 1))
        actual_value = self._extract_value_from_response(response_content, key)
        # Attempt type conversion for comparison
        try:
            expected_value = type(actual_value)(expected_value)
        except (ValueError, TypeError):
            pass
        success = actual_value == expected_value
        log_msg = f"Asserting: {key}, Expected: {expected_value}, Actual: {actual_value}"
        result = {"Result": "Pass" if success else "Fail"}
        self._log_result(success, log_msg)
        return result

    def _handle_db_checks(self, exp_result):
        """Handles database validation checks."""
        try:
            if exp_result.startswith('db_'):
                db_name = exp_result.split('.')[0]
                is_valid, msg = self.db_validator.validate_database_value(db_name, exp_result)
        except Exception as e:
            logging.error(f"{self.__class__.__name__}: Failed to validate database: {str(e)}")
        result = {"Result": "Pass" if is_valid else "Fail"}
        self._log_result(is_valid, msg)
        return result

    def _get_db_config_by_prefix(self, prefix: str) -> dict:
        db_config = self.db_configs.get(prefix.lower(), {})
        if not db_config:
            raise ValueError(f"No database configuration found for prefix: {prefix}")
        return db_config

    def _log_result(self, success: bool, message: str):
        """Logs the result of a check with appropriate color."""
        case_type = 'Sub Test'
        if self.is_main_test:
            case_type = 'Main Test'
        logging.debug(f"{self.__class__.__name__}: {message}")
        logger.info(
            ColorLogger.success(f"{case_type}=> {self.__class__.__name__}: {message}") if success else ColorLogger.error(f"{case_type}=> {self.__class__.__name__}: {message}"),
            html=True)


class ResponseFieldSaver(ResponseHandler):
    def __init__(self):
        super().__init__()
        self.variable_transformer = VariableTransformer()

    def save_fields_to_robot_variables(self, response: Union[str, Response], test_case: dict) -> None:
        response_content, _ = self.get_content_and_format(response)
        save_fields = test_case.get('Save Fields', '').splitlines()
        # Regular expression to match patterns like: assign_value($.result.amount,my_amount) or assign_value($.result.amount)
        transform_pattern = re.compile(r'^\s*(\w+)\(([^,]+)(?:,\s*([^)]+))?\)\s*$')

        for field in save_fields:
            if not field.strip():
                continue  # Skip empty lines
            field = field.strip()
            # Check if field matches transform format
            match = transform_pattern.match(field)
            if match:
                method_name, input_field, output_field = match.groups()
                # If no second parameter, use JSON Path as Robot variable name
                if output_field is None:
                    output_field = input_field
                input_value = self._extract_value_from_response(response_content, input_field)
                self.variable_transformer.transform_and_save(method_name, input_value, output_field)
            else:
                # Handle standard field format
                try:
                    value = self._extract_value_from_response(response_content, field)
                    field_name = f'{test_case["TCID"]}.{field.strip()}'
                    logger.info(ColorLogger.info(f"=> {self.__class__.__name__}: Setting global variable ${{{field_name}}} to {value}."), html=True)
                    BuiltIn().set_global_variable(f'${{{field_name}}}', value)
                except Exception as e:
                    logging.error(f"{self.__class__.__name__}: Failed to process field '{field}': {e}")
