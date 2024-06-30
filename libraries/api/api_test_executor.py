import os
from typing import Dict, List, Union, Any

from libraries.api.response_comparator import ResponseComparator
from libraries.common.config_manager import ConfigManager
from libraries.api.request_sender import RequestSender
from libraries.api.body_generator import BodyGenerator
from libraries.api.headers_generator import HeadersGenerator
from libraries.api.response_handler import ResponseHandler
from libraries.api.saved_fields_manager import SavedFieldsManager
from libraries.api.test_case_manager import TestCaseManager
from libraries.common.utility_helpers import UtilityHelpers, PROJECT_ROOT
from libraries.common.log_manager import logger


class APITestExecutor:
    def __init__(self, config_path: str = None, test_config_path: str = None, test_cases_path: str = None) -> None:
        self.project_root: str = PROJECT_ROOT
        self.config_path = config_path or os.path.join(self.project_root, 'configs', 'config.yaml')
        self.test_config_path = test_config_path or os.path.join(self.project_root, 'configs', 'test_config.yaml')

        self._load_configuration()
        self._initialize_components(test_cases_path)
        self._initialize_flags()

    def _load_configuration(self):
        self.config: Dict = ConfigManager.load_yaml(self.config_path)
        self.test_config: Dict = ConfigManager.load_yaml(self.test_config_path)
        self.active_environment: Dict = self.config['environments'][self.config['active_environment']]
        self.endpoints: Dict = self.active_environment['endpoints']

    def _initialize_components(self, test_cases_path: str):
        self.template_dir: str = os.path.join(self.project_root, 'configs', 'body_templates')
        self.headers_dir: str = os.path.join(self.project_root, 'configs', 'headers')
        self.body_defaults_dir: str = os.path.join(self.project_root, 'configs', 'body_defaults')

        self.saved_fields_manager: SavedFieldsManager = SavedFieldsManager()
        self.body_generator: BodyGenerator = BodyGenerator(self.template_dir, self.body_defaults_dir)
        self.headers_generator: HeadersGenerator = HeadersGenerator(self.headers_dir)
        self.response_handler: ResponseHandler = ResponseHandler()
        self.response_comparator: ResponseComparator = ResponseComparator()

        default_test_cases_path: str = os.path.join('test_cases', 'api_test_cases.xlsx')
        self.test_cases_path: str = test_cases_path or os.path.join(self.project_root, self.test_config.get('test_cases_path', default_test_cases_path))
        self.test_case_manager: TestCaseManager = TestCaseManager(self.test_cases_path, self.endpoints, self.headers_dir, self.template_dir, self.body_defaults_dir)

    def _initialize_flags(self):
        self.suite_setup_run = False
        self.suite_teardown_run = False

    @UtilityHelpers.time_calculation()
    def run_test_suite(self, tc_id_list: List[str] = None, tags: List[str] = None) -> None:
        tc_id_list = tc_id_list or self.test_config.get('tc_id_list', [])
        tags = tags or self.test_config.get('tags', [])

        try:
            filtered_cases = self.test_case_manager.filter_test_cases(tcid_list=tc_id_list, tags=tags)
            logger.debug(f"Successfully loaded test cases from {self.test_cases_path}")

            self._run_suite_setup(filtered_cases)
            self._run_test_cases(filtered_cases)
            self._run_suite_teardown(filtered_cases)
        except Exception as e:
            logger.info(f"Failed to run test suite: {str(e)}")
        finally:
            self.response_handler.apply_pending_operations()
            self.response_handler.generate_html_report()

    def _run_suite_setup(self, filtered_cases) -> None:
        for tc_id, test_case in filtered_cases.items():
            for test_step in test_case:
                if self._requires_condition(test_step, "[suite setup]"):
                    self._execute_condition(test_step, "[suite setup]", self._execute_setup_teardown)

    def _run_suite_teardown(self, filtered_cases) -> None:
        if not self.suite_teardown_run:
            for tc_id, test_case in filtered_cases.items():
                for test_step in test_case:
                    if self._requires_condition(test_step, "[suite teardown]"):
                        self._execute_condition(test_step, "[suite teardown]", self._execute_setup_teardown)
                        self.suite_teardown_run = True

    def _run_test_cases(self, filtered_cases) -> None:
        for tc_id, test_case in filtered_cases.items():
            self._run_test_setup(test_case)
            logger.info(f"Running test case {tc_id}")

            self._run_test_case(test_case, tc_id)
            logger.info(f"Test case {tc_id} ran successfully.")
            logger.info(f"********************************************\n")

            self._run_test_teardown(test_case)

    def _run_test_setup(self, test_case: List[Dict[str, Union[str, Any]]]) -> None:
        for test_step in test_case:
            if self._requires_condition(test_step, "[test setup]"):
                self._execute_condition(test_step, "[test setup]", self._execute_setup_teardown)

    def _run_test_teardown(self, test_case: List[Dict[str, Union[str, Any]]]) -> None:
        for test_step in test_case:
            if self._requires_condition(test_step, "[test teardown]"):
                self._execute_condition(test_step, "[test teardown]", self._execute_setup_teardown)

    def _requires_condition(self, test_step: Dict[str, Union[str, Any]], condition_tag: str) -> bool:
        conditions = test_step.get('Conditions', '').splitlines()
        return any(condition_tag in condition for condition in conditions)

    def _execute_condition(self, test_step, condition_tag, execution_func):
        conditions = test_step.get('Conditions', '').splitlines()
        for condition in conditions:
            if condition_tag in condition:
                condition_id = condition.split(condition_tag)[1].strip()
                logger.info(f"Running {condition_tag.strip('[]')} {condition_id}")
                execution_func(condition_id)
                logger.info(f"{condition_tag.strip('[]')} {condition_id} ran successfully.")

    def _execute_setup_teardown(self, tc_id: str) -> None:
        conditions = self.test_case_manager.get_conditions_by_tc_id(tc_id)
        for condition in conditions:
            if condition:
                test_step_result: bool = self._execute_test_step(condition)
                if not test_step_result:
                    raise Exception(f"Condition {tc_id} failed, skipping to the next case.")

    def _run_test_case(self, test_case: List[Dict[str, Union[str, Any]]], tc_id: str) -> None:
        for test_step in test_case:
            if self._requires_condition(test_step, "[check with]"):
                if not self._execute_test_step_with_dynamic_checks(test_step):
                    logger.info(f"Test case {tc_id} failed, skipping to next case.")
                    break
            else:
                if not self._execute_test_step(test_step):
                    logger.info(f"Test case {tc_id} failed, skipping to next case.")
                    break

    def _execute_test_step(self, test_step: Dict[str, Union[str, Any]], save_response: bool = False) -> Union[Dict[str, Any], str, None]:
        try:
            ex_ts_id: str = test_step['TSID']
            response, execution_time = self._send_request(test_step)
            result = self.response_handler.process_and_store_results(response, test_step, self.test_cases_path, self.test_case_manager, execution_time)
            logger.info(f"Finished execution of test step {ex_ts_id}")
            logger.info("============================================")
            return True if not save_response else self.response_handler.extract_response_content(response, test_step)
        except Exception as e:
            logger.error(f"Failed to execute test step {test_step['TSID']}: {str(e)}")
            return False

    def _send_request(self, test_step: Dict[str, Union[str, Any]]):
        ex_endpoint: str = test_step['Endpoint']
        current_endpoint: Union[Dict[str, Any], None] = self.endpoints.get(ex_endpoint, None)
        if current_endpoint is None:
            raise Exception(f"Endpoint {ex_endpoint} not found in config file")
        method: str = current_endpoint['method']
        url: str = current_endpoint['path']

        saved_fields: Dict[str, Any] = self.saved_fields_manager.load_saved_fields()
        headers: Dict[str, str] = self.headers_generator.prepare_headers(test_step['Headers'], saved_fields, test_step)
        self.saved_fields_manager.apply_saved_fields(test_step, saved_fields, ['Body Modifications', 'Exp Result'])
        body, format_type = self.body_generator.generate_request_body(test_step, test_step['Defaults'], method)

        response, execution_time = RequestSender.send_request(url, method, headers, body, format_type)
        return response, execution_time

    def _execute_test_step_with_dynamic_checks(self, test_step: Dict[str, Union[str, Any]]) -> bool:
        try:
            check_tc_ids = self._extract_check_tc_ids(test_step)
            pre_check_responses = self._execute_pre_check_steps(check_tc_ids)
            target_response = self._execute_test_step(test_step, save_response=True)
            post_check_responses = self._execute_post_check_steps(check_tc_ids)

            validate_result = self.response_comparator.validate_expectations(test_step, check_tc_ids, pre_check_responses, post_check_responses, target_response)
            self.response_handler.handle_validate_expectations_result(test_step, self.test_cases_path, self.test_case_manager, 0, validate_result)
            return validate_result
        except Exception as e:
            logger.error(f"Failed to execute test step {test_step['TSID']}: {str(e)}")
            return False

    def _extract_check_tc_ids(self, test_step: Dict[str, Union[str, Any]]) -> set:
        conditions = test_step.get('Conditions', '').splitlines()
        return {condition.split("[check with]")[1].strip() for condition in conditions if "[check with]" in condition}

    def _execute_pre_check_steps(self, check_tc_ids: set) -> Dict[str, Dict[str, Any]]:
        pre_check_responses = {}
        for check_tc_id in check_tc_ids:
            check_step = self.test_case_manager.get_conditions_by_tc_id(check_tc_id)[0]
            pre_check_responses[check_tc_id] = self._execute_test_step(check_step, save_response=True)
        return pre_check_responses

    def _execute_post_check_steps(self, check_tc_ids: set) -> Dict[str, Dict[str, Any]]:
        post_check_responses = {}
        for check_tc_id in check_tc_ids:
            check_step = self.test_case_manager.get_conditions_by_tc_id(check_tc_id)[0]
            post_check_responses[check_tc_id] = self._execute_test_step(check_step, save_response=True)
        return post_check_responses

