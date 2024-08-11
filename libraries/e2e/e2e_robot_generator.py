import logging
import os
from typing import Dict, List

import pandas as pd
from robot.api import TestSuite

from libraries.api.api_robot_generator import APIRobotCasesGenerator
from libraries.common.config_manager import ConfigManager
from libraries.common.utility_helpers import PROJECT_ROOT
from libraries.web.web_test_loader import WebTestLoader


class E2ERobotCasesGenerator:
    def __init__(self, test_config_path: str = None, test_cases_path: str = None):
        self.project_root: str = PROJECT_ROOT
        self.test_config_path = test_config_path or os.path.join(self.project_root, 'configs', 'e2e', 'e2e_test_config.yaml')
        self.env_config_path = os.path.join(self.project_root, 'configs', 'web', 'environments.yaml')
        self._load_configuration()
        self._initialize_components(test_cases_path)

    def _load_configuration(self):
        self.test_config: Dict = ConfigManager.load_yaml(self.test_config_path)

    def _initialize_components(self, test_cases_path: str):
        default_test_cases_path: str = os.path.join('test_cases', 'e2e_test_cases.xlsx')
        self.test_cases_path: str = test_cases_path or os.path.join(self.project_root, self.test_config.get('test_cases_path', default_test_cases_path))
        self.web_test_loader = WebTestLoader(self.test_cases_path)
        self.api_robot_generator = APIRobotCasesGenerator(None, self.test_cases_path)

    def create_test_suite(self, tc_id_list: List[str] = None, tags: List[str] = None) -> TestSuite:
        self.robot_suite = TestSuite('End To End TestSuite')

        tc_id_list = tc_id_list or self.test_config.get('tc_id_list', [])
        tags = tags or self.test_config.get('tags', [])
        test_cases = self.web_test_loader.filter_cases(tc_id_list, tags)
        for _, test_case in test_cases.iterrows():
            self.create_test_case(test_case)
        return self.robot_suite

    def create_test_case(self, test_case: Dict):
        logging.info(f"{self.__class__.__name__}: Creating E2E test case {test_case['Case ID']}")
        test_steps = self.web_test_loader.get_test_steps(test_case['Case ID'])
        test_data_sets = self.web_test_loader.get_test_data(test_case['Case ID'])
        if not test_data_sets:
            test_data_sets = [{}]
        self.child_suite = TestSuite(name=test_case['Case ID'], doc=test_case['Descriptions'])
        self.robot_suite.suites.append(self.child_suite)

        # Convert the paths to raw string format to avoid issues with backslashes
        env_config_path_arg = os.path.normpath(self.env_config_path).replace('\\', '/')
        test_config_path_arg = os.path.normpath(self.test_config_path).replace('\\', '/')
        test_cases_path_arg = os.path.normpath(self.test_cases_path).replace('\\', '/')
        self.child_suite.resource.imports.library('libraries.web.page_object.PageObject', args=[env_config_path_arg, test_config_path_arg, test_cases_path_arg])

        for data_set_index, data_set in enumerate(test_data_sets, 1):
            test_name = f"UI.{test_case['Case ID']}.{test_case['Name']}.{data_set_index}"
            robot_ui_test = self.child_suite.tests.create(name=test_name)
            if 'Tags' in test_case and pd.notna(test_case['Tags']):
                tags = [tag.strip() for tag in test_case['Tags'].split(',')]
                for tag in tags:
                    robot_ui_test.tags.add(tag)
            try:
                self.create_test_steps(robot_ui_test, test_steps, data_set)

                logging.info(f"{self.__class__.__name__}: E2E test case {test_case['Case ID']} with data set {data_set_index} created successfully")
            except Exception as e:
                logging.error(f"{self.__class__.__name__}: Error creating test case {test_case['Case ID']} with data set {data_set_index}: {str(e)}")
                raise

    def create_test_steps(self, robot_ui_test, test_steps: List[Dict], data_set: Dict):
        for _, step in test_steps.iterrows():
            page_name = step['Page Name']
            module_name = step['Module Name']
            parameters = self.extract_parameters(data_set, step['Parameter Name'])

            try:
                logging.info(f"{self.__class__.__name__}: Creating e2e step: {page_name}.{module_name}")
                if module_name == 'API':
                    self.child_suite.tests.remove(robot_ui_test)
                    self.child_suite.name = f"APISubSuite.{page_name}.{step['Case ID']}"
                    tc_id_list = step['Parameter Name'].split(',')
                    self.api_robot_generator.create_test_suite(tc_id_list, None, self.child_suite)

                else:
                    self.child_suite.name = f"UISubSuite.{page_name}.{step['Case ID']}"
                    robot_ui_test.body.create_keyword(name='execute_module', args=[page_name, module_name, parameters])
                    self.child_suite.teardown.config(name='close_browser', args=[])
            except Exception as e:
                logging.error(f"{self.__class__.__name__}: Error Creating web step {page_name}.{module_name}: {str(e)}")
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
                logging.warning(f"{E2ERobotCasesGenerator.__class__.__name__}: Parameter {name} not found in data set")
        logging.debug(f"{E2ERobotCasesGenerator.__class__.__name__}: Extracted parameters: {parameters}")
        return parameters
