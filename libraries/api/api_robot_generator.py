import logging
import os
from typing import Dict, List
import pandas as pd
from libraries.api.api_test_loader import APITestLoader
from libraries.common.config_manager import ConfigManager
from libraries.common.utility_helpers import PROJECT_ROOT
from robot.api import TestSuite, ResultWriter
from libraries.common.log_manager import logger_instance


class APIRobotCasesGenerator:
    def __init__(self, test_config_path: str = None, test_cases_path: str = None) -> None:
        self.project_root: str = PROJECT_ROOT
        self.test_config_path = test_config_path or os.path.join(self.project_root, 'configs', 'api_test_config.yaml')
        self._load_configuration()
        self._initialize_components(test_cases_path)

    def _load_configuration(self):
        self.test_config: Dict = ConfigManager.load_yaml(self.test_config_path)

    def _initialize_components(self, test_cases_path: str):
        default_test_cases_path: str = os.path.join('test_cases', 'api_test_cases.xlsx')
        self.test_cases_path: str = test_cases_path or os.path.join(self.project_root, self.test_config.get('test_cases_path', default_test_cases_path))
        self.test_cases_df = APITestLoader(self.test_cases_path)

    def create_test_suite(self, tc_id_list: List[str] = None, tags: List[str] = None, test_suite=None) -> TestSuite:
        self.api_suite = test_suite if test_suite else TestSuite('API TestSuite')
        self.api_suite.teardown.config(name='clear_saved_fields', args=[])
        test_cases_path_arg = os.path.normpath(self.test_cases_path).replace('\\', '/')
        logging.info(f"Generating API Robot Case：Currently using test cases from {test_cases_path_arg}")
        self.api_suite.resource.imports.library('libraries.api.api_test_keywords.APITestKeywords', args=[None, test_cases_path_arg])  # Update as needed
        tc_id_list = tc_id_list or self.test_config.get('tc_id_list', [])
        tags = tags or self.test_config.get('tags', [])
        try:
            filtered_cases = self.test_cases_df.filter_cases(tcid_list=tc_id_list, tags=tags)
            self.create_test_cases(filtered_cases)
        except Exception as e:
            logging.info(f"Generating API Robot Case：Failed to create test suite: {str(e)}")
        finally:
            return self.api_suite

    def create_test_cases(self, filtered_cases) -> None:
        for _, test_case in filtered_cases.iterrows():
            robot_api_test_name = f"API.{test_case['TCID']}.{test_case['Name']}"
            robot_api_test = self.api_suite.tests.create(name=robot_api_test_name, doc=test_case['Descriptions'])
            # Add tags
            if 'Tags' in test_case and pd.notna(test_case['Tags']):
                tags = [tag.strip() for tag in test_case['Tags'].split(',')]
                for tag in tags:
                    robot_api_test.tags.add(tag)

            robot_api_test.body.create_keyword(name='execute_api_test_case', args=[test_case['TCID']])

            # Add Test Setup and Test Teardown
            conditions = test_case['Conditions'].splitlines() if pd.notna(test_case['Conditions']) else []
            for condition in conditions:
                if '[TestSetup]' in condition:
                    case_ids = condition.strip('[TestSetup]').split(',')
                    robot_api_test.setup.config(name='execute_multiple_api_test_cases', args=[case_ids])
                if '[TestTeardown]' in condition:
                    case_ids = condition.strip('[TestTeardown]').split(',')
                    robot_api_test.teardown.config(name='execute_multiple_api_test_cases', args=[case_ids])
                if '[SuiteSetup]' in condition:
                    case_ids = condition.strip('[SuiteSetup]').split(',')
                    self.api_suite.setup.config(name='execute_multiple_api_test_cases', args=[case_ids])
                if '[SuiteTeardown]' in condition:
                    case_ids = condition.strip('[SuiteTeardown]').split(',')
                    self.api_suite.teardown.config(name='execute_multiple_api_test_cases', args=[case_ids])
