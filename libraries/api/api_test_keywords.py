import logging
import os
from typing import Dict, List, Union, Any
from libraries.common.config_manager import ConfigManager
from libraries.api.request_sender import RequestSender
from libraries.api.body_generator import BodyGenerator
from libraries.api.headers_generator import HeadersGenerator
from libraries.api.saved_fields_manager import SavedFieldsManager
from libraries.api.api_test_loader import APITestLoader
from libraries.common.utility_helpers import UtilityHelpers, PROJECT_ROOT
from robot.api.deco import keyword, library
from libraries.api.response_handler import APIResponseAsserter, APIResponseExtractor
from robot.libraries.BuiltIn import BuiltIn

builtin_lib = BuiltIn()


@library
class ApiTestKeywords:
    ROBOT_LIBRARY_SCOPE = 'TEST SUITE'

    def __init__(self, env_config_path: str = None, test_config_path: str = None, test_cases_path: str = None) -> None:
        self.project_root: str = PROJECT_ROOT
        self.env_config_path = env_config_path or os.path.join(self.project_root, 'configs', 'api', 'environments.yaml')
        self.test_config_path = test_config_path or os.path.join(self.project_root, 'configs', 'api', 'api_test_config.yaml')

        self._load_configuration(test_cases_path)
        self._initialize_components()
    def _load_configuration(self,test_cases_path):
        self.env_config: Dict = ConfigManager.load_yaml(self.env_config_path)
        self.test_config: Dict = ConfigManager.load_yaml(self.test_config_path)
        self.active_environment: Dict = self.env_config['environments'][self.test_config['active_environment']]
        self.endpoints: Dict = self.active_environment['endpoints']
        default_test_cases_path: str = os.path.join('test_cases', 'api_test_cases.xlsx')
        self.test_cases_path: str = test_cases_path or os.path.join(self.project_root, self.test_config.get('test_cases_path', default_test_cases_path))
    def _initialize_components(self):
        self.template_dir: str = os.path.join(self.project_root, 'configs', 'api', 'body_templates')
        self.headers_dir: str = os.path.join(self.project_root, 'configs', 'api', 'headers')
        self.body_defaults_dir: str = os.path.join(self.project_root, 'configs', 'api', 'body_defaults')

        self.saved_fields_manager: SavedFieldsManager = SavedFieldsManager()
        self.body_generator: BodyGenerator = BodyGenerator(self.template_dir, self.body_defaults_dir)
        self.headers_generator: HeadersGenerator = HeadersGenerator(self.headers_dir)
        self.api_response_asserter: APIResponseAsserter = APIResponseAsserter()
        self.api_response_extractor: APIResponseExtractor = APIResponseExtractor()




    @keyword
    def clear_saved_fields(self):
        if self.test_config.get('clear_saved_fields_after_test', False):
            self.saved_fields_manager.clear_saved_fields()
            logging.info("Cleared saved fields")
    @keyword
    def execute_multiple_api_test_cases(self, test_case_ids: List[str] = None):
        """
        Execute multiple API test cases.

        :param test_case_ids: List of test case IDs to execute. If None, all test cases will be executed.
        :return: Dictionary with test case IDs as keys and execution results as values.
        """
        api_test_loader = APITestLoader(self.test_cases_path)
        test_cases = api_test_loader.get_api_test_cases()

        if test_case_ids is None:
            test_case_ids = [tc['TCID'] for tc in test_cases]

        results = {}
        for tcid in test_case_ids:
            logging.info(f"Executing test case: {tcid}")
            result = self.execute_api_test_case(tcid)
            results[tcid] = result

        return results

    @keyword
    def execute_api_test_case(self, test_case_id: str, is_dynamic_check: bool = False):
        """
        Execute a single API test case by its ID.

        :param test_case_id: The ID of the test case to execute.
        :param is_dynamic_check: Boolean flag for dynamic check.
        :return: True if execution is successful, False otherwise. If is_dynamic_check is True, returns response and execution time.
        """
        try:
            # Load the specific test case
            api_test_loader = APITestLoader(self.test_cases_path)
            test_cases = api_test_loader.get_api_test_cases()
            test_case = next((tc for _, tc in test_cases.iterrows() if tc['TCID'] == test_case_id), None)

            if test_case is None:
                raise ValueError(f"Test case with ID {test_case_id} not found.")

            response, execution_time = self.send_request(test_case)
            logging.info(f"time taken to execute test case {test_case_id}: {execution_time}")
            self.api_response_asserter.assert_response(test_case['Exp Result'], response)
            self.api_response_extractor.extract_value(response, test_case)

            logging.info(f"Finished execution of test case {test_case_id}")
            logging.info("============================================")
            return True if not is_dynamic_check else (response, execution_time)
        except Exception as e:
            logging.error(f"Failed to execute test case {test_case_id}: {str(e)}")
            raise e
            return False

    def execute_api_test_case_with_dynamic_checks(self, test_step: Dict[str, Union[str, Any]]) -> bool:
        try:
            check_with_tc_ids = self._extract_check_with_tc_ids(test_step)
            pre_check_responses = self._execute_pre_check_steps(check_with_tc_ids)
            target_response, execution_time = self._execute_test_step(test_step, is_dynamic_check=True)
            post_check_responses = self._execute_post_check_steps(check_with_tc_ids)
            self.response_handler.process_step_results_with_dynamic_checks(check_with_tc_ids, target_response, pre_check_responses, post_check_responses, test_step,
                                                                           self.test_cases_path, self.test_case_manager, execution_time)
            return True
        except Exception as e:
            logging.error(f"Failed to execute test step {test_step['TSID']}: {str(e)}")
            raise e
            return False

    def send_request(self, test_case):
        ex_endpoint = test_case['Endpoint']
        current_endpoint = self.endpoints.get(ex_endpoint, None)
        if current_endpoint is None:
            raise Exception(f"Endpoint {ex_endpoint} not found in config file")
        method: str = current_endpoint['method']
        url: str = current_endpoint['path']

        saved_fields = self.saved_fields_manager.load_saved_fields()
        headers = self.headers_generator.prepare_headers(test_case, saved_fields)
        self.saved_fields_manager.apply_saved_fields(test_case, saved_fields)
        self.saved_fields_manager.apply_suite_variables(test_case)
        body, format_type = self.body_generator.generate_request_body(test_case, method)

        logging.info(f"Sending request to {url} with method: {method} for test step {test_case['TCID']}.")
        response, execution_time = RequestSender.send_request(url, method, headers, body, format_type)

        return response, execution_time
