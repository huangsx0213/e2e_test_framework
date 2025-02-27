import os
import logging
from typing import Dict, List
from robot.api import TestSuite
from libraries.common.config_manager import ConfigManager
from libraries.common.utility_helpers import PROJECT_ROOT
from libraries.robot.case.base_generator import RobotCaseGenerator
from libraries.performance.web_pt_loader import PerformanceTestLoader

class WebPerformanceRobotCaseGenerator(RobotCaseGenerator):
    def __init__(self, test_config_path: str = None, test_cases_path: str = None):
        self.project_root: str = PROJECT_ROOT
        self.test_config_path: str = test_config_path
        self.test_cases_path: str = test_cases_path
        self.test_config = None
        self.performance_test_loader = None
        self.robot_suite = None

    def load_configuration(self):
        try:
            self.test_config_path = (
                os.path.join(self.project_root, 'configs', 'web_pt_config.yaml')
                if self.test_config_path is None
                else self.test_config_path
            )
            self.test_config: Dict = ConfigManager.load_yaml(self.test_config_path)
        except FileNotFoundError:
            logging.error(f"{self.__class__.__name__}: Config file not found at {self.test_config_path}")
            raise
        except Exception as e:
            logging.error(f"{self.__class__.__name__}: Error loading configuration: {str(e)}")
            raise

    def initialize_components(self):
        try:
            default_test_cases_path: str = os.path.join('test_cases', 'web_pt_cases.xlsx')
            self.test_cases_path: str = (
                os.path.join(self.project_root, self.test_config.get('test_cases_path', default_test_cases_path))
                if self.test_cases_path is None
                else self.test_cases_path
            )

            if not os.path.exists(self.test_cases_path):
                logging.error(f"{self.__class__.__name__}: Test cases file not found at {self.test_cases_path}")
                raise FileNotFoundError(f"Test cases file does not exist: {self.test_cases_path}")

            self.performance_test_loader = PerformanceTestLoader(self.test_cases_path, self.test_config)
        except Exception as e:
            logging.error(f"{self.__class__.__name__}: Error initializing components: {str(e)}")
            raise

    def create_test_suite(self, tc_id_list: List[str] = None, tags: List[str] = None, parent_suite=None) -> TestSuite:
        try:
            self.robot_suite = TestSuite('Web Performance TestSuite')
            self._import_required_libraries(self.robot_suite)

            test_cases = self.performance_test_loader.get_test_cases()

            for _, test_case in test_cases.iterrows():
                if test_case['Run'] == 'Y':
                    self.create_test_case(self.robot_suite, test_case)

            self.robot_suite.setup.config(name='initialize_tester', args=[])
            self.robot_suite.teardown.config(name='finalize_and_close_tester', args=[])
            return self.robot_suite
        except Exception as e:
            logging.error(f"{self.__class__.__name__}: Error creating test suite: {str(e)}")
            raise RuntimeError(f"Failed to create test suite: {str(e)}")

    def create_test_case(self, suite, test_case: Dict):
        try:
            case_id = test_case['Case ID']
            test_name = f"Performance.{case_id}"
            robot_test = suite.tests.create(name=test_name, doc=test_case['Description'])
            self.create_test_steps(robot_test, case_id)
            logging.info(f"{self.__class__.__name__}: Test case {case_id} created successfully.")
        except Exception as e:
            logging.error(f"{self.__class__.__name__}: Error creating test case {test_case.get('Case ID', 'Unknown')}: {str(e)}")
            raise

    def create_test_steps(self, robot_test, case_id, test_steps=None, data_set=None):
        try:
            robot_test.body.create_keyword(name='execute_single_test', args=[case_id])
            robot_test.body.create_keyword(name='generate_reports', args=[case_id])
        except Exception as e:
            logging.error(f"{self.__class__.__name__}: Error creating test steps: {str(e)}")
            raise

    def _import_required_libraries(self, suite):
        try:
            suite.resource.imports.library('libraries.performance.web_pt_robot_keyword.RobotFrameworkWebTester')
        except Exception as e:
            logging.error(f"{self.__class__.__name__}: Error importing required libraries: {str(e)}")
            raise