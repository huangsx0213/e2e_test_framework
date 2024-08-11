import logging
import os
import re
import json
from typing import Dict, Any
from libraries.common.utility_helpers import UtilityHelpers
from .variable_generator import VariableGenerator
from robot.libraries.BuiltIn import BuiltIn

builtin_lib = BuiltIn()


class HeadersGenerator:
    def __init__(self, headers_dir: str) -> None:
        self.headers_dir: str = headers_dir
        self.format_json = UtilityHelpers.format_json

    def prepare_headers(self, testcase, saved_fields: Dict[str, Any]) -> Dict[str, str]:
        headers_filename = testcase['Headers']
        try:
            original_headers = self._load_headers(testcase)
            logging.info(
                f"{self.__class__.__name__}:Headers for test case '{testcase['TCID']}' loaded from file: \n{self.format_json(original_headers)}")
            headers = {k: self._replace_placeholders(v, saved_fields, testcase) for k, v in original_headers.items()}
            logging.info(f"{self.__class__.__name__}:Headers for test case '{testcase['TCID']}' replaced placeholders: \n{self.format_json(headers)}")
            return headers
        except KeyError as e:
            logging.error(f"{self.__class__.__name__}:Headers file '{headers_filename}' not found in test case '{testcase['TCID']}': {str(e)}")
            raise

        except json.JSONDecodeError as e:
            logging.error(
                f"{self.__class__.__name__}:Invalid JSON format in headers file '{headers_filename}' for test case '{testcase['TCID']}': {str(e)}")
            raise
        except Exception as e:
            logging.error(
                f"{self.__class__.__name__}:Error processing headers file '{headers_filename}' for test case '{testcase['TCID']}': {str(e)}")
            raise

    def _load_headers(self, testcase) -> Dict[str, str]:
        headers_filename = testcase['Headers']
        try:
            headers_file_path = os.path.join(self.headers_dir, headers_filename)
            if not headers_file_path.endswith('.json'):
                headers_file_path += '.json'
            if not os.path.exists(headers_file_path):
                logging.error(
                    f"{self.__class__.__name__}:Headers file '{headers_filename}' not found in directory '{self.headers_dir}' for test case '{testcase['TCID']}'")
                raise
            with open(headers_file_path, 'r') as file:
                headers = json.load(file)
            return headers
        except Exception as e:
            logging.error(
                f"{self.__class__.__name__}:Error loading headers file '{headers_filename}' for test case '{testcase['TCID']}': {str(e)}")
            raise

    def _replace_placeholders(self, value: Any, saved_fields: Dict[str, Any], testcase) -> Any:
        headers_filename = testcase['Headers']
        try:
            if isinstance(value, str):
                matches = re.findall(r'\{\{\s*([^}]+?)\s*\}\}', value)
                for match in matches:
                    if match in saved_fields:
                        value = value.replace(f'{{{{{match}}}}}', str([match]))
                        logging.info(f"{self.__class__.__name__}:Replaced {match} with saved field '{saved_fields[match]}' for test case '{testcase['TCID']}'")
                    else:
                        dynamic_value = VariableGenerator.generate_dynamic_value(match)
                        value = value.replace(f'{{{{{match}}}}}', str(dynamic_value))
                        logging.info(f"{self.__class__.__name__}:Replaced {match} with dynamic value '{dynamic_value}' for test case '{testcase['TCID']}'")

                matches = re.findall(r'\$\{([^}]+)\}', value)
                for match in matches:
                    replacement_value = builtin_lib.get_variable_value(f'${{{match}}}')
                    value = value.replace(match, str(replacement_value))
                    logging.info(f"{self.__class__.__name__}:Replaced {match} with variable value '{replacement_value}' for test case '{testcase['TCID']}'")

            return value
        except Exception as e:
            logging.error(
                f"{self.__class__.__name__}:Error replacing placeholders in headers file '{headers_filename}' for test case '{testcase['TCID']}': {str(e)}"
            )
            raise
