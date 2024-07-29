import logging
import os
from typing import Dict, List
import pandas as pd
from robot.api import TestSuite, ResultWriter
from libraries.api.api_test_loader import APITestLoader
from libraries.common.config_manager import ConfigManager
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

    def _initialize_components(self, test_cases_path: str):
        default_test_cases_path: str = os.path.join('test_cases', 'api_test_cases.xlsx')
        self.test_cases_path: str = test_cases_path or os.path.join(self.project_root, self.test_config.get('test_cases_path', default_test_cases_path))
        self.test_cases_df = APITestLoader(self.test_cases_path)

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
            return self.robot_suite

    def create_test_cases(self, filtered_cases) -> None:
        for _, test_case in filtered_cases.iterrows():
            robot_test = self.robot_suite.tests.create(name=test_case['TCID'] + '.' + test_case['Name'], doc=test_case['Descriptions'])
            # Add tags
            if 'Tags' in test_case and pd.notna(test_case['Tags']):
                tags = [tag.strip() for tag in test_case['Tags'].split(',')]
                for tag in tags:
                    robot_test.tags.add(tag)

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

