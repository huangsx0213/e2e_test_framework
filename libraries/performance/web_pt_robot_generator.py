import os
from robot.api import TestSuite
from libraries.common.config_manager import ConfigManager
from libraries.performance.web_pt_loader import PerformanceTestLoader
from libraries.common.utility_helpers import PROJECT_ROOT

class WebPerformanceRobotCasesGenerator:
    def __init__(self, test_config_path: str = None, test_cases_path: str = None):
        self.project_root = PROJECT_ROOT
        self.test_config_path = test_config_path or os.path.join(self.project_root, 'configs', 'web_pt_config.yaml')
        self.test_cases_path = test_cases_path or os.path.join(self.project_root, 'test_cases', 'web_pt_cases.xlsx')

        self._load_configuration()
        self._initialize_components()

    def _load_configuration(self):
        self.test_config = ConfigManager.load_yaml(self.test_config_path)

    def _initialize_components(self):
        self.performance_test_loader = PerformanceTestLoader(self.test_cases_path, self.test_config)

    def create_test_suite(self):
        # Create main test suite
        self.robot_suite = TestSuite('Web Performance TestSuite')
        self._import_required_libraries()

        # Load test cases
        test_cases = self.performance_test_loader.get_test_cases()

        for _, test_case in test_cases.iterrows():
            if test_case['Run'] == 'Y':
                case_id = test_case['Case ID']
                test_name = f"Performance.{case_id}"
                robot_test = self.robot_suite.tests.create(name=test_name, doc=test_case['Description'])

                # Create a single execute_single_test keyword for each test case
                robot_test.body.create_keyword(name='execute_single_test', args=[case_id])
                robot_test.body.create_keyword(name='generate_reports', args=[case_id])

        # Add setup and teardown for the entire suite
        self.robot_suite.setup.config(name='initialize_tester', args=[])
        self.robot_suite.teardown.config(name='close_tester', args=[])
        return self.robot_suite

    def _import_required_libraries(self):
        self.robot_suite.resource.imports.library(
            'libraries.performance.web_pt_robot_keyword.RobotFrameworkWebTester')
