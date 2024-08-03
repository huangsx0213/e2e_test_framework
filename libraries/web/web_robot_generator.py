import logging
import os
from typing import Dict, List

import pandas as pd
from robot.api import TestSuite
from libraries.common.config_manager import ConfigManager
from libraries.common.utility_helpers import PROJECT_ROOT
from libraries.web.web_test_loader import WebTestLoader
from libraries.common.log_manager import Logger
class WebUIRobotCasesGenerator:
    def __init__(self):
        self.config = self.load_config()
        self.web_test_loader = WebTestLoader(self.config['test_case_path'])
        self.robot_suite = TestSuite('WebUI Test Suite')
        self.robot_suite.resource.imports.library('libraries.web.page_object.PageObject')

    @staticmethod
    def load_config() -> Dict:
        config_path = os.path.join(PROJECT_ROOT, 'configs', 'web', 'web_config.yaml')
        return ConfigManager.load_yaml(config_path)

    def run_tests(self) -> TestSuite:
        test_cases = self.web_test_loader.get_test_cases()
        for _, test_case in test_cases.iterrows():
            if test_case['Run'] == 'Y':
                self.execute_test_case(test_case)
        return self.robot_suite

    def execute_test_case(self, test_case: Dict):
        logging.info(f"Starting E2E test case {test_case['Case ID']}")
        test_steps = self.web_test_loader.get_test_steps(test_case['Case ID'])
        test_data_sets = self.web_test_loader.get_test_data(test_case['Case ID'])

        for data_set_index, data_set in enumerate(test_data_sets, 1):
            test_name = f"{test_case['Case ID']}.{test_case['Name']}.{data_set_index}"
            robot_test = self.robot_suite.tests.create(name=test_name, doc=test_case['Descriptions'])
            if 'Tags' in test_case and pd.notna(test_case['Tags']):
                tags = [tag.strip() for tag in test_case['Tags'].split(',')]
                for tag in tags:
                    robot_test.tags.add(tag)
            try:
                logging.info(f"Running E2E test case {test_case['Case ID']} with data set {data_set_index}")
                self.execute_test_steps(robot_test, test_steps, data_set)
                logging.info(f"Completed E2E test case {test_case['Case ID']} with data set {data_set_index}")
            except Exception as e:
                logging.error(f"Error executing test case {test_case['Case ID']} with data set {data_set_index}: {str(e)}")
                robot_test.status = 'FAIL'
                robot_test.message = str(e)
            finally:
                self.cleanup_test_environment()

    def execute_test_steps(self, robot_test, test_steps: List[Dict], data_set: Dict):
        for _, step in test_steps.iterrows():
            page_name = step['Page Name']
            module_name = step['Module Name']
            parameters = self.extract_parameters(data_set, step['Parameter Name'])

            try:
                logging.info(f"Executing web step: {page_name}.{module_name}")
                robot_test.body.create_keyword(name='execute_module', args=[page_name, module_name, parameters])
            except Exception as e:
                logging.error(f"Error executing step {page_name}.{module_name}: {str(e)}")
                raise

    @staticmethod
    def extract_parameters(data_set: Dict, parameter_names: str) -> Dict:
        parameters = {}
        for name in parameter_names.split(','):
            if name in data_set:
                value = data_set[name]
                # Add type conversion here if needed
                parameters[name] = value
            else:
                logging.warning(f"Parameter {name} not found in data set")
        logging.debug(f"Extracted parameters: {parameters}")
        return parameters

    def cleanup_test_environment(self):
        # Add cleanup logic here
        pass

