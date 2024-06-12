import json
import re
from datetime import datetime
import pandas as pd
import requests
from openpyxl.styles import Font
from openpyxl import load_workbook
from typing import Dict, Any, Union
from libraries import logger
import xmltodict
from libraries.excel_operation_manager import ExcelOperationManager
from libraries.html_report_generator import HTMLReportGenerator
from libraries.saved_fields_manager import SavedFieldsManager


class ResponseHandler:
    def __init__(self) -> None:
        self.workbook_cache = {}
        self.pending_operations = []
        self.sfm = SavedFieldsManager()
        self.html_report_generator = HTMLReportGenerator(logger.html_log_entries)
        self.excel_manager = ExcelOperationManager()

    def process_and_store_results(self, response: requests.Response, test_step, test_cases_path: str,
                                  test_case_manager, execution_time: float) -> None:
        try:
            actual_status: int = response.status_code
            actual_response: Union[Dict[str, Any], str] = self._extract_response_content(response)

            # actual_results
            expected_lines = self._split_lines(test_step['Exp Result'])
            results = [self.compare_response_field(actual_response, expectation) for expectation in expected_lines]
            actual_results = self.format_comparison_results(results)

            # overall_result
            overall_result = "FAIL" if any(res['result'] == "FAIL" for res in results) else "PASS"

            # fields to save to excel and yaml
            fields_to_save_lines = self._split_lines(test_step['Save Fields'])
            fields_saved_results = [self.get_save_result(actual_response, field) for field in fields_to_save_lines]
            fields_to_save_for_excel = self.format_fields_to_save(fields_saved_results)
            fields_to_save_for_yaml = self.format_fields_to_save_yaml(test_step, fields_saved_results)
            self.sfm.save_fields(fields_to_save_for_yaml)

            # Cache the operation
            self.excel_manager.cache_excel_operation(test_step, test_cases_path, actual_status, actual_results,
                                                     overall_result, fields_to_save_for_excel, test_case_manager,
                                                     execution_time)

            logger.log("INFO", json.dumps(results, indent=4))
            logger.log("INFO", f"The Result is: {overall_result}.")
            return overall_result
        except Exception as e:
            logger.log("ERROR", f"An error occurred while processing and storing results: {str(e)}")
            raise

    def apply_pending_operations(self) -> None:
        self.excel_manager.apply_pending_operations()

    def generate_html_report(self):
        self.html_report_generator.generate_html_report(self.pending_operations)

    def _extract_response_content(self, response: requests.Response) -> Union[Dict[str, Any], str]:
        try:
            return response.json()
        except json.JSONDecodeError as json_error:
            logger.log("Warning", f"JSON decode error: {json_error}. Attempting XML parse.")
            try:
                return xmltodict.parse(response.text)
            except Exception as xml_error:
                logger.log("ERROR", f"XML parse error: {xml_error}. Returning raw response text.")
                return response.text

    def compare_response_field(self, actual_response: Union[Dict[str, Any], str], expectation: str) -> Dict[str, Any]:
        if expectation:
            try:
                field_path, expected_value = expectation.split('=')
            except ValueError:
                return self.create_error_comparison_result(expectation, "Invalid [Exp Result] format")

            expected_value = expected_value.strip().strip('""').strip("''")
            actual_value = self.extract_actual_value(actual_response, field_path)

            if actual_value is None:
                return self.create_error_comparison_result(field_path, "Field not found")
            return self.create_comparison_result(field_path, actual_value, expected_value)
        else:
            self.create_not_specified_result()

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

        if isinstance(actual_response, list) and 'response[' in parts[0]:
            match = re.match(r'response\[(\d+)\]', parts[0])
            array_index = int(match.group(1))
            actual_response = actual_response[array_index]
        try:
            return _extract_value(actual_response, parts[1:])
        except (KeyError, IndexError, TypeError) as e:
            logger.log("ERROR", f"Error retrieving the value for path '{field_path}': {str(e)}")
            return None

    def format_comparison_results(self, results: list) -> str:
        return '\n'.join(f"{res['field']}={res['actual_value']}:{res['result']}" for res in results)

    def format_fields_to_save(self, fields_saved_results: list) -> str:
        return '\n'.join(f"{res['field']}={res['actual_value']}" for res in fields_saved_results)

    def format_fields_to_save_yaml(self, test_step, fields_saved_results: list) -> str:
        return {
            f"{test_step['TSID']}.{res['field']}": res['actual_value'] for res in fields_saved_results
        }

    def _split_lines(self, lines: str) -> list:
        return lines.strip().split('\n') if pd.notna(lines) else []

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
            "expected_value": "N/A",
            "result": "Not specified"
        }

    def create_save_result(self, field_path, actual_value) -> Dict[str, Any]:
        return {
            "field": field_path,
            "actual_value": actual_value
        }
