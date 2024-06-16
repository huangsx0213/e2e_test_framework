import os
from typing import Dict, List, Union, Any
from libraries.config_manager import ConfigManager
from libraries.request_sender import RequestSender
from libraries.body_generator import BodyGenerator
from libraries.headers_generator import HeadersGenerator
from libraries.response_handler import ResponseHandler
from libraries.saved_fields_manager import SavedFieldsManager
from libraries.test_case_manager import TestCaseManager
from libraries.utility_helpers import UtilityHelpers
from libraries.log_manager import logger_instance, logger


class APITestExecutor:
    def __init__(self, config_path: str = 'configs/config.yaml',
                 test_config_path: str = 'configs/test_config.yaml') -> None:
        self.test_cases_path: Union[str, None] = None
        self.test_case_manager: Union[TestCaseManager, None] = None

        # Load configuration
        self.config: Dict = ConfigManager.load_yaml(config_path)
        self.test_config: Dict = ConfigManager.load_yaml(test_config_path)
        self.active_environment: Dict = self.config['environments'][self.config['active_environment']]
        self.endpoints: Dict = self.active_environment['endpoints']

        # Load other configurations
        self.template_dir: str = 'configs/body_templates'
        self.headers_dir: str = 'configs/headers'
        self.body_defaults_dir: str = 'configs/body_defaults'

        # Initialize other components
        self.saved_fields_manager: SavedFieldsManager = SavedFieldsManager()
        self.body_generator: BodyGenerator = BodyGenerator(self.template_dir, self.body_defaults_dir)
        self.headers_generator: HeadersGenerator = HeadersGenerator(self.headers_dir)
        self.response_handler: ResponseHandler = ResponseHandler()

        # Flags to track if suite-level setup and teardown have been run
        self.suite_setup_run = False
        self.suite_teardown_run = False

    @UtilityHelpers.time_calculation()
    def run_test_suite(self, test_cases_path: str = None, tc_id_list: List[str] = None, tags: List[str] = None) -> None:
        test_cases_path = test_cases_path or self.test_config.get('test_cases_path', 'test_cases/test_cases.xlsx')
        tc_id_list = tc_id_list or self.test_config.get('tc_id_list', [])
        tags = tags or self.test_config.get('tags', [])
        self.test_cases_path = test_cases_path

        try:
            self.test_case_manager = TestCaseManager(test_cases_path, self.endpoints, self.headers_dir,
                                                     self.template_dir, self.body_defaults_dir)
            filtered_cases = self.test_case_manager.filter_test_cases(tcid_list=tc_id_list, tags=tags)
            logger.debug(f"Successfully loaded test cases from {test_cases_path}")
            # Run suite-level setup if defined
            self.run_suite_setup(filtered_cases)

            for tc_id, test_case in filtered_cases.items():
                # Run test-level setup if defined
                self.run_test_setup(test_case)
                logger.info(f"Running test case {tc_id}")

                self.run_test_case(test_case, tc_id)
                logger.info(f"Test case {tc_id} ran successfully.")
                logger.info(f"********************************************\n")

                # Run test-level teardown if defined
                self.run_test_teardown(test_case)

            # Run suite-level teardown if defined
            self.run_suite_teardown(filtered_cases)

        except Exception as e:
            logger.info(f"Failed to run test suite: {str(e)}")
        finally:
            # Perform delayed Excel operations after all test cases are executed or an error is encountered
            self.response_handler.apply_pending_operations()
            self.response_handler.generate_html_report()

    def run_suite_setup(self, filtered_cases) -> None:
        for tc_id, test_case in filtered_cases.items():
            for test_step in test_case:
                conditions = test_step['Conditions'].splitlines() if test_step.get('Conditions') else []
                for condition in conditions:
                    if "[suite setup]" in condition and not self.suite_setup_run:
                        suite_tc_id = condition.split("[suite setup]")[1].strip()
                        logger.info(f"Running suite-level setup {suite_tc_id}")
                        self.execute_setup_teardown(suite_tc_id)
                        logger.info(f"Suite-level setup {suite_tc_id} ran successfully.")
                        self.suite_setup_run = True

    def run_suite_teardown(self, filtered_cases) -> None:
        if self.suite_teardown_run:
            return
        for tc_id, test_case in filtered_cases.items():
            for test_step in test_case:
                conditions = test_step['Conditions'].splitlines() if test_step.get('Conditions') else []
                for condition in conditions:
                    if "[suite teardown]" in condition:
                        suite_tc_id = condition.split("[suite teardown]")[1].strip()
                        logger.info(f"Running suite-level teardown {suite_tc_id}")
                        self.execute_setup_teardown(suite_tc_id)
                        logger.info(f"Suite-level teardown {suite_tc_id} ran successfully.")
                        self.suite_teardown_run = True

    def run_test_setup(self, test_case: List[Dict[str, Union[str, Any]]]) -> None:
        for test_step in test_case:
            conditions = test_step['Conditions'].splitlines() if test_step.get('Conditions') else []
            for condition in conditions:
                if "[test setup]" in condition:
                    test_tc_id = condition.split("[test setup]")[1].strip()
                    logger.info(f"Running test-level setup {test_tc_id}")
                    self.execute_setup_teardown(test_tc_id)
                    logger.info(f"Test-level setup {test_tc_id} ran successfully.")

    def run_test_teardown(self, test_case: List[Dict[str, Union[str, Any]]]) -> None:
        for test_step in test_case:
            conditions = test_step['Conditions'].splitlines() if test_step.get('Conditions') else []
            for condition in conditions:
                if "[test teardown]" in condition:
                    test_tc_id = condition.split("[test teardown]")[1].strip()
                    logger.info(f"Running test-level teardown {test_tc_id}")
                    self.execute_setup_teardown(test_tc_id)
                    logger.info(f"Test-level teardown {test_tc_id} ran successfully.")

    def execute_setup_teardown(self, tc_id: str) -> None:
        conditions = self.test_case_manager.get_conditions_by_tc_id(tc_id)
        for condition in conditions:
            if condition:
                test_step_result: bool = self.execute_test_step(condition)
                if not test_step_result:
                    raise Exception(f"Condition {tc_id} failed, skipping to the next case.")

    def run_test_case(self, test_case: List[Dict[str, Union[str, Any]]], tc_id: str) -> None:
        for test_step in test_case:
            test_step_result = self.execute_test_step(test_step)
            if not test_step_result:
                logger.info(f"Test case {tc_id} failed, skipping to next case.")
                break

    @UtilityHelpers.time_calculation()
    def execute_test_step(self, test_step: Dict[str, Union[str, Any]]) -> bool:
        try:
            ex_ts_id: str = test_step['TSID']
            # logger_instance.set_context(ts_id=ex_ts_id, result='Pending')
            ex_endpoint: str = test_step['Endpoint']
            ex_headers: str = test_step['Headers']
            ex_defaults_body: str = test_step['Defaults']
            ex_body_modifications: str = test_step['Body Modifications']
            ex_exp_result: str = test_step['Exp Result']
            ex_fields_to_save: str = test_step['Save Fields']
            logger.info(f"Starting execution of test step {ex_ts_id}")
            current_endpoint: Union[Dict[str, Any], None] = self.endpoints.get(ex_endpoint, None)
            if current_endpoint is None:
                raise Exception(f"Endpoint {ex_endpoint} not found in config file")
            method: str = current_endpoint['method']
            logger.debug(f"Executing test step {ex_ts_id} with method {method} and endpoint [{ex_endpoint}]")
            url: str = current_endpoint['path']
            logger.debug(f"Executing test step {ex_ts_id} with URL {url}")
            # Load saved fields
            saved_fields: Dict[str, Any] = self.saved_fields_manager.load_saved_fields()
            # Prepare headers
            headers: Dict[str, str] = self.headers_generator.prepare_headers(ex_headers, saved_fields, test_step)
            # Apply saved fields to [Body Modifications] and [Exp Result]
            self.saved_fields_manager.apply_saved_fields(test_step, saved_fields, ['Body Modifications', 'Exp Result'])
            # Prepare request body
            body, format_type = self.body_generator.generate_request_body(test_step, ex_defaults_body, method)
            # Log request

            # Send request and log response
            response, execution_time = RequestSender.send_request(url, method, headers, body, format_type)

            # Process response
            result = self.response_handler.process_and_store_results(response, test_step, self.test_cases_path,
                                                                     self.test_case_manager, execution_time)

            test_result = 'pass' if result == 'PASS' else 'fail'

            logger.info(f"Finished execution of test step {ex_ts_id}")
            logger.info("============================================")
            return True
        except Exception as e:
            logger.error(f"Failed to execute test step {ex_ts_id}: {str(e)}")
            return False
