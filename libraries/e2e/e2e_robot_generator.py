import logging
import os
from typing import Dict, List
import pandas as pd
from robot.api import TestSuite
from libraries.common.config_manager import ConfigManager
from libraries.common.utility_helpers import PROJECT_ROOT
from libraries.web.web_test_loader import WebTestLoader
from libraries.common.log_manager import Logger
from libraries.api.api_robot_generator import APIRobotCasesGenerator

class E2ERobotCasesGenerator:
    def __init__(self, test_config_path: str = None, test_cases_path: str = None):
        self.project_root: str = PROJECT_ROOT
        self.test_config_path = test_config_path or os.path.join(self.project_root, 'configs', 'e2e', 'e2e_test_config.yaml')
        self.env_config_path = os.path.join(self.project_root, 'configs', 'e2e', 'environments.yaml')
        self._load_configuration()
        self._initialize_components(test_cases_path)

    def _load_configuration(self):
        self.test_config: Dict = ConfigManager.load_yaml(self.test_config_path)

    def _initialize_components(self, test_cases_path: str):
        default_test_cases_path: str = os.path.join('test_cases', 'e2e_test_cases.xlsx')
        self.test_cases_path: str = test_cases_path or os.path.join(self.project_root, self.test_config.get('test_cases_path', default_test_cases_path))
        self.web_test_loader = WebTestLoader(self.test_cases_path)
        self.api_robot_generator = APIRobotCasesGenerator()

    def create_test_suite(self, tc_id_list: List[str] = None, tags: List[str] = None) -> TestSuite:
        self.robot_suite = TestSuite('End to End Test Suite')
        self.robot_suite.resource.imports.library('libraries.web.page_object.PageObject', args=[self.env_config_path,self.test_config_path,self.test_cases_path])
        tc_id_list = tc_id_list or self.test_config.get('tc_id_list', [])
        tags = tags or self.test_config.get('tags', [])
        test_cases = self.web_test_loader.filter_cases(tc_id_list, tags)
        for _, test_case in test_cases.iterrows():
            self.create_test_case(test_case)
        self.robot_suite.teardown.config(name='close_browser', args=[])
        return self.robot_suite

    def create_test_case(self, test_case: Dict):
        logging.info(f"Creating E2E test case {test_case['Case ID']}")
        test_steps = self.web_test_loader.get_test_steps(test_case['Case ID'])
        test_data_sets = self.web_test_loader.get_test_data(test_case['Case ID'])
        if not test_data_sets:
            test_data_sets = [{}]
        for data_set_index, data_set in enumerate(test_data_sets, 1):
            test_name = f"{test_case['Case ID']}.{test_case['Name']}.{data_set_index}"

            robot_test = self.robot_suite.tests.create(name=test_name, doc=test_case['Descriptions'])
            if 'Tags' in test_case and pd.notna(test_case['Tags']):
                tags = [tag.strip() for tag in test_case['Tags'].split(',')]
                for tag in tags:
                    robot_test.tags.add(tag)
            try:
                self.create_test_steps(robot_test, test_steps, data_set)
                logging.info(f"E2E test case {test_case['Case ID']} with data set {data_set_index} created successfully")
            except Exception as e:
                logging.error(f"Error creating test case {test_case['Case ID']} with data set {data_set_index}: {str(e)}")
                raise

    def create_test_steps(self, robot_test, test_steps: List[Dict], data_set: Dict):
        for _, step in test_steps.iterrows():
            page_name = step['Page Name']
            module_name = step['Module Name']
            parameters = self.extract_parameters(data_set, step['Parameter Name'])

            try:
                logging.info(f"Creating e2e step: {page_name}.{module_name}")
                if module_name == 'API':
                    tc_id_list = step['Parameter Name'].split(',')
                    ts = self.api_robot_generator.create_test_suite(tc_id_list)
                    robot_test.body.add_suite(ts)
                else:
                    robot_test.body.create_keyword(name='execute_module', args=[page_name, module_name, parameters])
            except Exception as e:
                logging.error(f"Error Creating web step {page_name}.{module_name}: {str(e)}")
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
