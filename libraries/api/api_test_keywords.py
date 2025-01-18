import logging
import os
import re
from time import sleep
from typing import Dict, List, Any
import pandas as pd
from libraries.common.config_manager import ConfigManager
from libraries.common.db_validator import DBValidator
from libraries.common.utility_helpers import PROJECT_ROOT
from libraries.api.request_sender import RequestSender
from libraries.api.body_generator import BodyGenerator
from libraries.api.headers_generator import HeadersGenerator
from libraries.api.saved_fields_manager import SavedFieldsManager
from libraries.api.response_handler import ResponseValidator, ResponseFieldSaver
from libraries.api.api_test_loader import APITestLoader
from robot.libraries.BuiltIn import BuiltIn
from robot.api.deco import keyword, library
from libraries.common.variable_transformer import VariableTransformer
from libraries.robot.api_report_generator import HTMLReportGenerator

builtin_lib = BuiltIn()


@library
class APITestKeywords:
    ROBOT_LIBRARY_SCOPE = 'TEST SUITE'

    def __init__(self, test_config_path: str = None, test_cases_path: str = None) -> None:
        self.project_root: str = PROJECT_ROOT
        self._load_configuration(test_config_path, test_cases_path)
        self._initialize_components()

    def _load_configuration(self, test_config_path, test_cases_path):

        self.test_config_path = test_config_path or os.path.join(self.project_root, 'configs', 'api_test_config.yaml')

        self.test_config: Dict = ConfigManager.load_yaml(self.test_config_path)

        default_test_cases_path: str = os.path.join('test_cases', 'api_test_cases.xlsx')
        self.test_cases_path: str = test_cases_path or os.path.join(self.project_root, self.test_config.get('test_cases_path', default_test_cases_path))

        self.active_environment = self.test_config['active_environment']
        self.db_configs = self.test_config.get('database', {}).get(self.active_environment, {})
        if not self.db_configs:
            raise ValueError(f"No database configuration for environment: {self.active_environment}")

    def _load_endpoints(self):
        endpoints = self.api_test_loader.get_endpoints()
        self.endpoints = {}
        for _, row in endpoints[endpoints['Environment'] == self.active_environment].iterrows():
            self.endpoints[row['Endpoint']] = {
                'method': row['Method'],
                'path': row['Path']
            }

    def _initialize_components(self):
        self.saved_fields_manager: SavedFieldsManager = SavedFieldsManager()
        self.api_test_loader = APITestLoader(self.test_cases_path)
        self._load_endpoints()
        self.body_generator: BodyGenerator = BodyGenerator(self.api_test_loader)
        self.headers_generator: HeadersGenerator = HeadersGenerator(self.api_test_loader)
        self.api_response_validator: ResponseValidator = ResponseValidator()
        self.response_field_saver: ResponseFieldSaver = ResponseFieldSaver()
        self.variable_transformer = VariableTransformer()
        self.db_validator = DBValidator()

    @keyword
    def api_sanity_check(self) -> None:
        skip_on_sanity_check_failure = BuiltIn().get_variable_value('${skip_on_sanity_check_failure}', default=False)
        if skip_on_sanity_check_failure:
            BuiltIn().skip("Skipping current test as sanity check failed.")
        else:
            logging.info(f"{self.__class__.__name__}: Sanity check succeeded, continuing with the test.")

    @keyword
    def clear_saved_fields(self):
        if self.test_config.get('clear_saved_fields_after_test', False):
            self.saved_fields_manager.clear_saved_fields()
            logging.info(f"{self.__class__.__name__}: Cleared saved fields")

    @keyword
    def execute_conditions_cases(self, conditions_case_ids: List[str] = None):
        results = {}
        for tcid in conditions_case_ids:
            logging.info(f"{self.__class__.__name__}: Executing test case: {tcid}")
            result = self.execute_api_test_case(tcid)
            results[tcid] = result

        return results

    @keyword
    def execute_conditions_cases_with_transformer(self, original_tcid, setup_case_ids: List[str] = None):

        test_cases = APITestLoader(self.test_cases_path).get_api_test_cases()

        # Execute function transformations before creating the test case
        test_case = test_cases.loc[test_cases['TCID'] == original_tcid].to_dict('records')[0]
        self._transformer_handler(test_case)

        results = {}
        for setup_id in setup_case_ids:
            logging.info(f"{self.__class__.__name__}: Executing setup test case: {setup_id}")
            result = self.execute_api_test_case(setup_id)
            results[setup_id] = result

        return results

    @keyword
    def execute_api_test_case(self, test_case_id: str, is_dynamic_check: bool = False):
        try:
            test_cases = APITestLoader(self.test_cases_path).get_api_test_cases()
            test_case = next((tc for _, tc in test_cases.iterrows() if tc['TCID'] == test_case_id), None)

            if test_case is None:
                raise ValueError(f"{self.__class__.__name__}: Test case with ID {test_case_id} not found.")

            check_with_tcids = self._extract_check_with_tcids(test_case)

            if check_with_tcids:
                pre_check_responses = self._execute_check_with_cases(check_with_tcids)
                response, execution_time = self._execute_single_test_case(test_case)
                logging.info("============================================")
                post_check_responses = self._execute_check_with_cases(check_with_tcids)
                self.api_response_validator.validate(test_case, response, pre_check_responses, post_check_responses)
            else:
                response, execution_time = self._execute_single_test_case(test_case)
                self.api_response_validator.validate(test_case, response)

            logging.info(f"{self.__class__.__name__}: Finished execution of test case {test_case_id}")
            logging.info("============================================")

            return True if not is_dynamic_check else (response, execution_time)
        except Exception as e:
            logging.error(f"{self.__class__.__name__}: Failed to execute test case {test_case_id}: {str(e)}")
            raise e

    def _execute_single_test_case(self, test_case):
        response, execution_time = self.send_request(test_case)
        logging.info(f"{self.__class__.__name__}: Time taken to execute test case {test_case['TCID']}: {execution_time:.2f} seconds")
        # self.api_response_validator.validate_response(test_case, response)
        self.response_field_saver.save_fields_to_robot_variables(response, test_case)
        self.validate_data_base(test_case)
        wait = float(test_case['Wait']) if test_case['Wait'] != '' else 0
        if wait > 0:
            sleep(wait)
            logging.info(f"{self.__class__.__name__}: Waiting for results of {test_case['TCID']} in {wait} seconds.")

        return response, execution_time

    def validate_data_base(self, test_case):
        try:
            for line in test_case['Exp Result'].splitlines():
                if line.strip().startswith('db_'):
                    prefix = line.strip().split('.')[0]
                    db_config = self._get_db_config_by_prefix(prefix)
                    if not db_config:
                        raise ValueError(f"No database configuration found for prefix: {prefix}")
                    self.db_validator.setup_database(db_config)
                    self.db_validator.validate_database_value(line.strip())
        except Exception as e:
            logging.error(f"{self.__class__.__name__}: Failed to validate database: {str(e)}")
            raise e

    def _get_db_config_by_prefix(self, prefix: str) -> dict:
        db_config = self.db_configs.get(prefix.lower(), {})
        if not db_config:
            raise ValueError(f"No database configuration found for prefix: {prefix}")
        return db_config

    def _extract_check_with_tcids(self, test_case):
        conditions = test_case['Conditions']
        if pd.isna(conditions):
            return []

        check_with_match = re.search(r'\[Checkwith\](.*)', conditions)
        if check_with_match:
            return [tcid.strip() for tcid in check_with_match.group(1).split(',')]
        return []

    def _execute_check_with_cases(self, check_with_tcids):
        responses = {}
        for tcid in check_with_tcids:
            logging.info(f"{self.__class__.__name__}: Executing test case {tcid} for dynamic check")
            response, _ = self.execute_api_test_case(tcid, is_dynamic_check=True)
            responses[tcid] = response
        return responses

    def send_request(self, test_case):
        ex_endpoint = test_case['Endpoint']
        current_endpoint = self.endpoints.get(ex_endpoint, None)
        if current_endpoint is None:
            raise Exception(f"{self.__class__.__name__}: Endpoint {ex_endpoint} not found in config file")
        method: str = current_endpoint['method']
        url: str = current_endpoint['path']

        saved_fields = self.saved_fields_manager.load_saved_fields()
        headers = self.headers_generator.prepare_headers(test_case, saved_fields)
        self.saved_fields_manager.apply_saved_fields(test_case, saved_fields)
        self.saved_fields_manager.apply_suite_variables(test_case)
        body, format_type = self.body_generator.generate_request_body(test_case, method)

        logging.info(f"{self.__class__.__name__}: Sending request to {url} with method: {method} for test step {test_case['TCID']}.")
        response, execution_time = RequestSender.send_request(url, method, headers, body, format_type)

        return response, execution_time

    def _transformer_handler(self, test_case: Dict[str, Any]) -> None:
        transformers = test_case.get('Variable Transform', '').splitlines()
        transformers_data = []
        for transformer in transformers:
            match = re.findall(r'(\w*)\((.*?)\s*(?:,\s*(.*?))?\)', transformer.strip())
            if match:
                function_name, input_field, output_field = match[0]
                transformers_data.append((function_name.strip(), input_field.strip(), output_field.strip() if output_field else None))

        self.variable_transformer.transform(transformers_data, test_case)
        logging.info(f"{self.__class__.__name__}: Transformed variables for test case {test_case['TCID']}.")
        logging.info("=" * 100)

    @keyword
    def generate_report(self):
        """Generates and logs the test report as an HTML file, embedded in the Robot Framework log."""
        report_generator = HTMLReportGenerator(self.api_response_validator.test_results)
        html_content = report_generator.generate_html_report()

        # Save the HTML report to a file
        report_file = os.path.join(self.project_root, "report", "test_report.html")
        os.makedirs(os.path.dirname(report_file), exist_ok=True)  # Ensure the directory exists
        with open(report_file, "w", encoding="utf-8") as f:
            f.write(html_content)
        logging.info(f"Test report saved to: {report_file}")
