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
from libraries.response_comparator import ResponseComparator
from libraries.saved_fields_manager import SavedFieldsManager


class ResponseHandler:
    def __init__(self) -> None:
        self.workbook_cache = {}
        self.pending_operations = []
        self.sfm = SavedFieldsManager()
        self.html_report_generator = HTMLReportGenerator(logger.html_log_entries)
        self.excel_manager = ExcelOperationManager()
        self.comparator = ResponseComparator()

    def process_and_store_results(self, response: requests.Response, test_step, test_cases_path: str,
                                  test_case_manager, execution_time: float) -> None:
        try:
            actual_status: int = response.status_code
            actual_response: Union[Dict[str, Any], str] = self.comparator.extract_response_content(response)

            # actual_results
            expected_lines = self._split_lines(test_step['Exp Result'])
            results = [self.comparator.compare_response_field(actual_response, expectation) for expectation in
                       expected_lines]
            actual_results = self.format_comparison_results(results)

            # overall_result
            overall_result = "FAIL" if any(res['result'] == "FAIL" for res in results) else "PASS"

            # fields to save to excel and yaml
            fields_to_save_lines = self._split_lines(test_step['Save Fields'])
            fields_saved_results = [self.comparator.get_save_result(actual_response, field) for field in
                                    fields_to_save_lines]
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
        self.pending_operations = self.excel_manager.apply_pending_operations()


    def generate_html_report(self):
        self.html_report_generator.generate_html_report(self.pending_operations)

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
