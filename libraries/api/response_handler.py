import json
import pandas as pd
import requests
from typing import Dict, Any, Union
from libraries.common.log_manager import logger
from libraries.api.excel_operation_manager import ExcelOperationManager
from libraries.api.html_report_generator import HTMLReportGenerator
from libraries.api.response_comparator import ResponseComparator
from libraries.api.saved_fields_manager import SavedFieldsManager


class ResponseHandler:
    def __init__(self) -> None:
        self.workbook_cache = {}
        self.pending_operations = []
        self.sfm = SavedFieldsManager()
        self.html_report_generator = HTMLReportGenerator()
        self.excel_manager = ExcelOperationManager()
        self.response_comparator = ResponseComparator()

    def process_step_results(self, response: requests.Response, test_step, test_cases_path: str,
                             test_case_manager, execution_time: float, is_dynamic_check: bool) -> str:
        try:
            fields_to_save_for_excel = ''
            actual_status: int = response.status_code
            actual_response: Union[Dict[str, Any], str] = self.response_comparator.extract_response_content(response, test_step)

            # actual_results
            expected_lines = self._split_lines(test_step['Exp Result'])
            results = [self.response_comparator.compare_response_field(actual_response, expectation) for expectation in
                       expected_lines]
            actual_results = self.format_comparison_results(results)

            # overall_result
            overall_result = "FAIL" if any(res['result'] == "FAIL" for res in results) else "PASS"

            # fields to save to excel and yaml
            fields_to_save_lines = self._split_lines(test_step['Save Fields'])
            if fields_to_save_lines != ['']:
                fields_saved_results = [self.response_comparator.get_save_result(actual_response, field) for field in fields_to_save_lines]
                fields_to_save_for_excel = self.format_fields_to_save(fields_saved_results)
                fields_to_save_for_yaml = self.format_fields_to_save_yaml(test_step, fields_saved_results)
                self.sfm.save_fields(fields_to_save_for_yaml)

            # Cache the operation
            if not is_dynamic_check:
                self.excel_manager.cache_excel_operation(test_step, test_cases_path, actual_status, actual_results,
                                                         overall_result, fields_to_save_for_excel, test_case_manager,
                                                         execution_time)

            logger.info(json.dumps(results, indent=4))
            logger.info(f"The Result is: {overall_result}.")
            return overall_result
        except Exception as e:
            logger.error(f"An error occurred while processing and storing results: {str(e)}")
            raise

    def process_step_results_with_dynamic_checks(self, check_tc_ids, target_response, pre_check_responses, post_check_responses, test_step, test_cases_path, test_case_manager,
                                                 execution_time) -> None:
        try:
            actual_status: int = target_response.status_code
            validate_result = self.response_comparator.compare_response_field_with_dynamic_checks(test_step, check_tc_ids, pre_check_responses, post_check_responses,
                                                                                                  target_response)
            overall_result = "FAIL" if any(res['result'] == "FAIL" for res in validate_result) else "PASS"
            actual_results = self.format_comparison_results_with_dynamic_checks(validate_result)
            # Cache the operation for writing to Excel
            self.excel_manager.cache_excel_operation(test_step, test_cases_path, actual_status, actual_results,
                                                     overall_result, actual_results, test_case_manager,
                                                     execution_time)
        except Exception as e:
            logger.error(f"An error occurred while handling validate expectations result: {str(e)}")
            raise

    def apply_pending_operations(self) -> None:
        self.pending_operations = self.excel_manager.apply_pending_operations()

    def generate_html_report(self) -> None:
        self.html_report_generator.generate_html_report(self.pending_operations)

    def format_comparison_results(self, results: list) -> str:
        return '\n'.join(f"{res['field']}={res['actual_value']}:{res['result']}" for res in results)

    def format_comparison_results_with_dynamic_checks(self, results: list) -> str:
        formatted_results = []
        for res in results:
            if res['field'].startswith('response'):
                r = f"{res['field']}={res['actual_value']}:{res['result']}"
                formatted_results.append(r)
            else:
                r = f"{res['field']}=+{res['actual_value']}:{res['result']}" if res['actual_value'] >= 0 else f"{res['field']}=-{res['actual_value']}:{res['result']}"
                formatted_results.append(r)

        return '\n'.join(formatted_results)

    def format_fields_to_save(self, fields_saved_results: list) -> str:
        return '\n'.join(f"{res['field']}={res['actual_value']}" for res in fields_saved_results)

    def format_fields_to_save_yaml(self, test_step, fields_saved_results: list) -> Dict[str, Any]:
        return {
            f"{test_step['TSID']}.{res['field']}": res['actual_value'] for res in fields_saved_results
        }

    def _split_lines(self, lines: str) -> list:
        return lines.strip().split('\n') if pd.notna(lines) else []
