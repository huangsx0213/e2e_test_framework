import os
import logging
from typing import Dict, List
import pandas as pd
from robot.api import TestSuite
from libraries.common.config_manager import ConfigManager
from libraries.common.utility_helpers import PROJECT_ROOT
from libraries.web.web_test_loader import WebTestLoader
from libraries.robot.case.base_generator import RobotCaseGenerator
from libraries.robot.case.api_generator import APIRobotCaseGenerator

class E2ERobotCaseGenerator(RobotCaseGenerator):
    def __init__(self, test_config_path: str = None, test_cases_path: str = None):
        self.project_root: str = PROJECT_ROOT
        self.test_config_path: str = test_config_path
        self.test_cases_path: str = test_cases_path
        self.test_config = None
        self.web_test_loader = None
        self.api_robot_generator = None
        self.robot_suite = None
        self.main_suite = None
        self.case_suite = None

    def load_configuration(self):
        """Load configuration from YAML file"""
        try:
            self.test_config_path = (
                os.path.join(self.project_root, 'configs', 'e2e_test_config.yaml')
                if self.test_config_path is None
                else self.test_config_path
            )
            self.test_config: Dict = ConfigManager.load_yaml(self.test_config_path)
            logging.info(f"{self.__class__.__name__}: Configuration loaded successfully")
        except FileNotFoundError:
            logging.error(f"{self.__class__.__name__}: Config file not found at {self.test_config_path}")
            raise
        except Exception as e:
            logging.error(f"{self.__class__.__name__}: Error loading configuration: {str(e)}")
            raise

    def initialize_components(self):
        """Initialize test loaders and other components"""
        try:
            default_test_cases_path: str = os.path.join('test_cases', 'e2e_test_cases.xlsx')
            self.test_cases_path: str = (
                os.path.join(self.project_root, self.test_config.get('test_cases_path', default_test_cases_path))
                if self.test_cases_path is None
                else self.test_cases_path
            )

            if not os.path.exists(self.test_cases_path):
                logging.error(f"{self.__class__.__name__}: Test cases file not found at {self.test_cases_path}")
                raise FileNotFoundError(f"Test cases file does not exist: {self.test_cases_path}")

            self.web_test_loader = WebTestLoader(self.test_cases_path, self.test_config)
            self.api_robot_generator = APIRobotCaseGenerator(None, self.test_cases_path)
            self.api_robot_generator.load_configuration()
            self.api_robot_generator.initialize_components()
            logging.info(f"{self.__class__.__name__}: Components initialized successfully")
        except Exception as e:
            logging.error(f"{self.__class__.__name__}: Error initializing components: {str(e)}")
            raise

    def create_test_suite(self, tc_id_list: List[str] = None, tags: List[str] = None, parent_suite=None) -> TestSuite:
        """Create test suite with hierarchical structure"""
        try:
            self.robot_suite = TestSuite('End To End TestSuite')
            self._import_required_libraries(self.robot_suite)
            self.robot_suite.setup.config(name='set_environment_variables', args=[])

            tc_id_list = tc_id_list or self.test_config.get('tc_id_list', [])
            tags = tags or self.test_config.get('tags', [])
            test_cases = self.web_test_loader.filter_cases(tc_id_list, tags)

            if test_cases.empty:
                logging.warning(f"{self.__class__.__name__}: No test cases found matching criteria.")
                return self.robot_suite

            for _, test_case in test_cases.iterrows():
                suite_name = test_case['Suite']
                case_id = test_case['Case ID']

                # Create or get main suite layer
                if suite_name not in [suite.name for suite in self.robot_suite.suites]:
                    self.main_suite = self.robot_suite.suites.create(name=suite_name)
                    self._import_required_libraries(self.main_suite)
                else:
                    self.main_suite = next(suite for suite in self.robot_suite.suites if suite.name == suite_name)

                # Create or get case ID suite layer
                case_suite_name = f"Case_{case_id}"
                if case_suite_name not in [suite.name for suite in self.main_suite.suites]:
                    self.case_suite = self.main_suite.suites.create(name=case_suite_name)
                    self._import_required_libraries(self.case_suite)
                else:
                    self.case_suite = next(suite for suite in self.main_suite.suites if suite.name == case_suite_name)

                self.create_test_case(self.case_suite, test_case)

            self.robot_suite.teardown.config(name='close_browser', args=[])
            return self.robot_suite
        except Exception as e:
            logging.error(f"{self.__class__.__name__}: Error creating test suite: {str(e)}")
            raise RuntimeError(f"Failed to create test suite: {str(e)}")

    def create_test_case(self, suite, test_case: Dict):
        """Create test case with data sets"""
        try:
            case_id = test_case['Case ID']
            test_steps = self.web_test_loader.get_test_steps(case_id)
            test_data_sets = self.web_test_loader.get_test_data(case_id)

            if not test_data_sets:
                logging.warning(f"{self.__class__.__name__}: No data sets found for test case {case_id}. Using empty data")
                test_data_sets = [{}]

            for data_set_index, data_set in enumerate(test_data_sets, 1):
                test_name = f"{case_id}.{data_set_index}"
                robot_test = suite.tests.create(name=test_name, doc=test_case['Descriptions'])
                robot_test.body.create_keyword(name='sanity_check', args=[])

                if 'Tags' in test_case and pd.notna(test_case['Tags']):
                    tags = [tag.strip() for tag in test_case['Tags'].split(',')]
                    for tag in tags:
                        robot_test.tags.add(tag)

                self.create_test_steps(robot_test, test_steps, data_set)
                logging.info(f"{self.__class__.__name__}: Test case {case_id}.{data_set_index} created successfully")

        except Exception as e:
            logging.error(f"{self.__class__.__name__}: Error creating test case {test_case.get('Case ID', 'Unknown')}: {str(e)}")
            raise

    def create_test_steps(self, robot_test, test_steps: List[Dict], data_set: Dict):
        """Create test steps for both UI and API tests"""
        try:
            for _, step in test_steps.iterrows():
                if step['Run'] == 'Y':
                    page_name = step['Page Name']
                    module_name = step['Module Name']

                    if module_name == 'API':
                        self._generate_api_step(step, robot_test)
                    else:
                        self._generate_ui_step(robot_test, page_name, module_name, data_set)

        except Exception as e:
            logging.error(f"{self.__class__.__name__}: Error creating test steps: {str(e)}")
            raise

    def _import_required_libraries(self, suite):
        """Import required Robot Framework libraries"""
        try:
            test_config_path_arg = os.path.normpath(self.test_config_path).replace(os.path.sep, '/')
            test_cases_path_arg = os.path.normpath(self.test_cases_path).replace(os.path.sep, '/')
            suite.resource.imports.library('libraries.robot.robot_test_executor.RobotTestExecutor', args=[test_config_path_arg, test_cases_path_arg])
        except Exception as e:
            logging.error(f"{self.__class__.__name__}: Error importing required libraries: {str(e)}")
            raise

    def _generate_api_step(self, step, robot_test):
        """Generate API test steps using APIRobotCasesGenerator"""
        try:
            self.case_suite.tests.remove(robot_test)
            tc_id_list = step['APIs'].split(',')
            self.api_robot_generator.create_test_suite(tc_id_list, None, self.case_suite)
        except Exception as e:
            logging.error(f"{self.__class__.__name__}: Error generating API step: {str(e)}")
            raise

    def _generate_ui_step(self, robot_test, page_name: str, module_name: str, params: Dict):
        """Generate UI test steps"""
        try:
            robot_test.body.create_keyword(name='execute_module', args=[page_name, module_name, params])
        except Exception as e:
            logging.error(f"{self.__class__.__name__}: Error generating UI step for {page_name}.{module_name}: {str(e)}")
            raise