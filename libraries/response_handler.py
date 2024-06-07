import json
import re
import pandas as pd
import requests
from jinja2 import Environment, FileSystemLoader
from openpyxl.styles import Font
from openpyxl import load_workbook
from typing import Dict, Any, Union
from libraries import logger
import xmltodict
from libraries.saved_fields_manager import SavedFieldsManager


class ResponseHandler:
    def __init__(self) -> None:
        self.workbook_cache = {}
        self.pending_operations = []
        self.sfm = SavedFieldsManager()

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
            self.cache_excel_operation(test_step, test_cases_path, actual_status, actual_results,
                                       overall_result, fields_to_save_for_excel, test_case_manager,
                                       execution_time)

            logger.log("INFO", json.dumps(results, indent=4))
            logger.log("INFO", f"The Result is: {overall_result}.")
        except Exception as e:
            logger.log("ERROR", f"An error occurred while processing and storing results: {str(e)}")
            raise

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

    def cache_excel_operation(self, test_step, file_path: str, actual_status: int,
                              formatted_results: str, overall_result: str,
                              formatted_fields_saved: str, test_case_manager,
                              execution_time: float) -> None:
        self.pending_operations.append({
            "tcid": test_step.get('TCID'),  # 添加TCID
            "test_step": test_step,  # 修改为test_steps
            "file_path": file_path,
            "actual_status": actual_status,
            "formatted_results": formatted_results,
            "overall_result": overall_result,
            "formatted_fields_saved": formatted_fields_saved,
            "test_case_manager": test_case_manager,
            "execution_time": execution_time
        })

    def apply_pending_operations(self) -> None:
        for operation in self.pending_operations:
            self.apply_excel_operation(**operation)

        # Save all workbooks in the cache
        for file_path, workbook in self.workbook_cache.items():
            workbook.save(file_path)

    def apply_excel_operation(self, tcid, test_step, file_path: str, actual_status: int,
                              formatted_results: str, overall_result: str,
                              formatted_fields_saved: str, test_case_manager,
                              execution_time: float) -> None:
        if file_path not in self.workbook_cache:
            try:
                self.workbook_cache[file_path] = load_workbook(file_path)
            except Exception as e:
                logger.log("ERROR", f"Failed to load workbook: {str(e)}")
                raise
        try:
            workbook = self.workbook_cache[file_path]
            sheet = workbook.active
            actual_status_col_idx = self.get_excel_column_index(sheet, "Act Status")
            actual_result_col_idx = self.get_excel_column_index(sheet, "Act Result")
            overall_result_col_idx = self.get_excel_column_index(sheet, "Result")
            fields_saved_col_idx = self.get_excel_column_index(sheet, "Saved Fields")
            api_execution_time_col_idx = self.get_excel_column_index(sheet, "API Timing")

            row = test_case_manager.get_row_index_by_tsid(test_step["TSID"]) + 2
            sheet.cell(row=row, column=actual_status_col_idx, value=actual_status)
            sheet.cell(row=row, column=actual_result_col_idx, value=formatted_results)
            overall_cell = sheet.cell(row=row, column=overall_result_col_idx, value=overall_result)

            overall_cell.font = Font(color="006400" if overall_result == "PASS" else "8B0000")
            sheet.cell(row=row, column=fields_saved_col_idx, value=formatted_fields_saved)
            api_timing_cell = sheet.cell(row=row, column=api_execution_time_col_idx, value=f"{execution_time:.2f}s")
            if execution_time > 5:
                api_timing_cell.font = Font(color="8B0000")
            else:
                api_timing_cell.font = Font(color="006400")


        except Exception as e:
            logger.log("ERROR", f"An error occurred while writing results to the Excel file: {str(e)}")
            raise

    def get_excel_column_index(self, sheet, column_name: str) -> int:
        try:
            for col in sheet.iter_cols(1, sheet.max_column):
                if col[0].value == column_name:
                    return col[0].column
        except Exception as e:
            logger.log("ERROR", f"An error occurred while getting the column index for '{column_name}': {str(e)}")
            return None

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

    def generate_html_report(self, report_path: str):
        try:
            env = Environment(loader=FileSystemLoader('configs/body_templates'))
            template = env.get_template('report_template.html')

            results = []
            for operation in self.pending_operations:
                test_step = operation['test_step']  # 获取test_step
                results.append({
                    'tcid': test_step['TCID'],
                    'tsid': test_step['TSID'],
                    'endpoint': test_step['Endpoint'],
                    'status': operation['actual_status'],
                    'result': operation['overall_result'],
                    'expected_result': test_step['Exp Result'],
                    'actual_result': operation['formatted_results'],
                    'saved_fields': operation['formatted_fields_saved'],
                    'execution_time': f"{operation['execution_time']:.2f}s"
                })

            html_content = template.render(results=results)
            with open(report_path, 'w') as report_file:
                report_file.write(html_content)
        except Exception as e:
            logger.log("ERROR", f"Failed to generate HTML report: {str(e)}")
            raise
