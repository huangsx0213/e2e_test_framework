import logging
import os
from typing import Dict, List
import pandas as pd
from libraries.common.config_manager import ConfigManager
from libraries.api.body_generator import BodyGenerator
from libraries.api.headers_generator import HeadersGenerator
from libraries.api.saved_fields_manager import SavedFieldsManager
from libraries.api.api_test_loader import APITestLoader
from libraries.common.utility_helpers import PROJECT_ROOT
from robot.api import TestSuite, ResultWriter
from libraries.common.log_manager import logger_instance

class APITestExecutor:
    def __init__(self, config_path: str = None, test_config_path: str = None, test_cases_path: str = None) -> None:
        self.project_root: str = PROJECT_ROOT
        self.config_path = config_path or os.path.join(self.project_root, 'configs', 'api', 'config.yaml')
        self.test_config_path = test_config_path or os.path.join(self.project_root, 'configs', 'api', 'test_config.yaml')

        self._load_configuration()
        self._initialize_components(test_cases_path)

    def _load_configuration(self):
        self.config: Dict = ConfigManager.load_yaml(self.config_path)
        self.test_config: Dict = ConfigManager.load_yaml(self.test_config_path)
        self.active_environment: Dict = self.config['environments'][self.config['active_environment']]
        self.endpoints: Dict = self.active_environment['endpoints']

    def _initialize_components(self, test_cases_path: str):
        self.template_dir: str = os.path.join(self.project_root, 'configs', 'api', 'body_templates')
        self.headers_dir: str = os.path.join(self.project_root, 'configs', 'api', 'headers')
        self.body_defaults_dir: str = os.path.join(self.project_root, 'configs', 'api', 'body_defaults')

        self.saved_fields_manager: SavedFieldsManager = SavedFieldsManager()
        self.body_generator: BodyGenerator = BodyGenerator(self.template_dir, self.body_defaults_dir)
        self.headers_generator: HeadersGenerator = HeadersGenerator(self.headers_dir)


        default_test_cases_path: str = os.path.join('test_cases', 'api_test_cases.xlsx')
        self.test_cases_path: str = test_cases_path or os.path.join(self.project_root, self.test_config.get('test_cases_path', default_test_cases_path))
        self.test_cases_df = APITestLoader(self.test_cases_path)
        if self.test_config.get('clear_saved_fields_on_init', False):
            self.saved_fields_manager.clear_saved_fields()

    def create_test_suite(self, tc_id_list: List[str] = None, tags: List[str] = None) -> None:
        self.robot_suite = TestSuite('API Test Suite')
        self.robot_suite.resource.imports.library('libraries.api.api_test_keywords.APITestRunner')  # Update as needed
        tc_id_list = tc_id_list or self.test_config.get('tc_id_list', [])
        tags = tags or self.test_config.get('tags', [])
        try:
            filtered_cases = self.test_cases_df.filter_cases(tcid_list=tc_id_list, tags=tags)
            logging.info(f"Successfully loaded test cases from {self.test_cases_path}")
            self.create_test_cases(filtered_cases)
        except Exception as e:
            logging.info(f"Failed to run test suite: {str(e)}")
        finally:
            #self.response_handler.apply_pending_operations()
            #self.response_handler.generate_html_report()
            return self.robot_suite
    def create_test_cases(self, filtered_cases) -> None:
        for _, test_case in filtered_cases.iterrows():
            robot_test = self.robot_suite.tests.create(name=test_case['TCID'] + '.' + test_case['Name'], doc=test_case['Descriptions'])

            robot_test.body.create_keyword(name='execute_api_test_case', args=[test_case['TCID']])

            # Add Test Setup and Test Teardown
            conditions = test_case['Conditions'].splitlines() if pd.notna(test_case['Conditions']) else []
            for condition in conditions:
                if '[TestSetup]' in condition:
                    case_ids = condition.strip('[TestSetup]').split(',')
                    robot_test.setup.config(name='execute_multiple_api_test_cases', args=[case_ids])
                elif '[TestTeardown]' in condition:
                    case_ids = condition.strip('[TestTeardown]').split(',')
                    robot_test.teardown.config(name='execute_multiple_api_test_cases', args=[case_ids])
                elif '[SuiteSetup]' in condition:
                    case_ids = condition.strip('[SuiteSetup]').split(',')
                    self.robot_suite.setup.config(name='execute_multiple_api_test_cases', args=[case_ids])
                elif '[SuiteTeardown]' in condition:
                    case_ids = condition.strip('[SuiteTeardown]').split(',')
                    self.robot_suite.teardown.config(name='execute_multiple_api_test_cases', args=[case_ids])



def run_test_suite(suite):
    # Run the test suite and generate output XML
    suite.run(output='output.xml')

    # Generate log and report
    ResultWriter('output.xml').write_results(
        report='report.html',
        log='log.html'
    )


if __name__ == "__main__":
    te = APITestExecutor()
    # Create and run the test suite
    suite = te.create_test_suite(['TC001', 'TC002'], ['tag1'])
    run_test_suite(suite)