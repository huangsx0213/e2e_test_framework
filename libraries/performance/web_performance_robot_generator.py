import os
from robot.api import TestSuite
from libraries.common.config_manager import ConfigManager
from libraries.common.utility_helpers import PROJECT_ROOT
from libraries.web.web_test_loader import WebTestLoader

class WebPerformanceRobotCasesGenerator:
    def __init__(self, test_config_path: str = None, test_cases_path: str = None):
        self.project_root = PROJECT_ROOT
        self.test_config_path = test_config_path or os.path.join(self.project_root, 'configs', 'web_test_config.yaml')
        self.test_cases_path = test_cases_path or os.path.join(self.project_root, 'test_cases', 'web_performance_test_cases.xlsx')

        self._load_configuration()
        self._initialize_components()

    def _load_configuration(self):
        self.test_config = ConfigManager.load_yaml(self.test_config_path)

    def _initialize_components(self):
        self.web_test_loader = WebTestLoader(self.test_cases_path, self.test_config)

    def create_test_suite(self):
        # Create main test suite
        self.robot_suite = TestSuite('Web Performance TestSuite')
        self._import_required_libraries()