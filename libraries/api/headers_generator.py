import os
import re
import json
from typing import Dict, Any
from libraries.common.log_manager import logger
from libraries.common.utility_helpers import UtilityHelpers
from .variable_generator import VariableGenerator


class HeadersGenerator:
    def __init__(self, headers_dir: str) -> None:
        self.headers_dir: str = headers_dir
        self.format_json = UtilityHelpers.format_json

    def prepare_headers(self, headers_filename: str, saved_fields: Dict[str, Any], test_step: Dict[str, Any]) -> Dict[
        str, str]:
        try:
            original_headers = self._load_headers(headers_filename, test_step)
            logger.info(
                f"[TSID:{test_step['TSID']}] Headers for test step '{test_step['TSID']}' loaded from file: \n{self.format_json(original_headers)}")
            headers = {k: self._replace_placeholders(v, saved_fields, headers_filename, test_step) for k, v in
                       original_headers.items()}
            logger.info(
                f"[TSID:{test_step['TSID']}] Headers for test step '{test_step['TSID']}' replaced placeholders: \n{self.format_json(headers)}")
            return headers
        except KeyError as e:
            logger.error(f"[TSID:{test_step['TSID']}] Headers file '{headers_filename}' not found in test step '{test_step['TSID']}': {str(e)}")
            raise

        except json.JSONDecodeError as e:
            logger.error(
                f"[TSID:{test_step['TSID']}] Invalid JSON format in headers file '{headers_filename}' for test step '{test_step['TSID']}': {str(e)}")
            raise
        except Exception as e:
            logger.error(
                f"[TSID:{test_step['TSID']}] Error processing headers file '{headers_filename}' for test step '{test_step['TSID']}': {str(e)}")
            raise

    def _load_headers(self, headers_filename: str, test_step: Dict[str, Any]) -> Dict[str, str]:
        try:
            headers_file_path = os.path.join(self.headers_dir, headers_filename)
            if not headers_file_path.endswith('.json'):
                headers_file_path += '.json'
            if not os.path.exists(headers_file_path):
                logger.error(
                    f"[TSID:{test_step['TSID']}] Headers file '{headers_filename}' not found in directory '{self.headers_dir}' for test step '{test_step['TSID']}'")
                raise
            with open(headers_file_path, 'r') as file:
                headers = json.load(file)
            return headers
        except Exception as e:
            logger.error(
                f"[TSID:{test_step['TSID']}] Error loading headers file '{headers_filename}' for test step '{test_step['TSID']}': {str(e)}")
            raise

    def _replace_placeholders(self, value: Any, saved_fields: Dict[str, Any], headers_filename: str, test_step: Dict[str, Any]) -> Any:
        try:
            if isinstance(value, str):
                matches = re.findall(r'\{\{\s*([^}]+?)\s*\}\}', value)
                for match in matches:
                    if match in saved_fields:
                        value = value.replace(f'{{{{{match}}}}}', str([match]))
                    else:
                        dynamic_value = VariableGenerator.generate_dynamic_value(match)
                        value = value.replace(f'{{{{{match}}}}}', str(dynamic_value))
            return value
        except Exception as e:
            logger.error(
                f"[TSID:{test_step['TSID']}] Error replacing placeholders in headers file '{headers_filename}' for test step '{test_step['TSID']}': {str(e)}"
            )
            raise
