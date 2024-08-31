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
    def __init__(self, test_config_path: str = None, test_cases_path: str = None):
        self.project_root: str = PROJECT_ROOT
        self.test_config_path = test_config_path or os.path.join(self.project_root, 'configs',  'web_test_config.yaml')
        self._load_configuration()
        self._initialize_components(test_cases_path)

    def _load_configuration(self):
        self.test_config: Dict = ConfigManager.load_yaml(self.test_config_path)

    def _initialize_components(self, test_cases_path: str):
        default_test_cases_path: str = os.path.join('test_cases', 'web_test_cases.xlsx')
        self.test_cases_path: str = test_cases_path or os.path.join(self.project_root, self.test_config.get('test_cases_path', default_test_cases_path))
        self.web_test_loader = WebTestLoader(self.test_cases_path)

    def create_test_suite(self, tc_id_list: List[str] = None, tags: List[str] = None) -> TestSuite:
        self.robot_suite = TestSuite('Web UI TestSuite')
        self.robot_suite.resource.imports.library('libraries.web.page_object.PageObject')
        tc_id_list = tc_id_list or self.test_config.get('tc_id_list', [])
        tags = tags or self.test_config.get('tags', [])
        test_cases = self.web_test_loader.filter_cases(tc_id_list, tags)
        for _, test_case in test_cases.iterrows():
            self.create_test_case(test_case)
        self.robot_suite.teardown.config(name='close_browser', args=[])
        return self.robot_suite

    def create_test_case(self, test_case: Dict):
        logging.info(f"{self.__class__.__name__}: Creating E2E test case {test_case['Case ID']}")
        test_steps = self.web_test_loader.get_test_steps(test_case['Case ID'])
        test_data_sets = self.web_test_loader.get_test_data(test_case['Case ID'])

        if not test_data_sets:
            # If no test data sets, create a single test case with empty parameters
            test_data_sets = [{}]
            logging.warning(f"{self.__class__.__name__}: No test data sets found for {test_case['Case ID']}, creating a single test case with empty parameters")
            logging.warning(f"{self.__class__.__name__}: Need to check if all steps of {test_case['Case ID']} are valid for empty parameters")

        for data_set_index, data_set in enumerate(test_data_sets, 1):
            test_name = f"UI.{test_case['Case ID']}.{test_case['Name']}.{data_set_index}"
            robot_test = self.robot_suite.tests.create(name=test_name, doc=test_case['Descriptions'])
            robot_test.body.create_keyword(name='sanity_check', args=[f"Skip current test {test_case['Case ID']} due to Sanity Check failure"])
            if 'Tags' in test_case and pd.notna(test_case['Tags']):
                tags = [tag.strip() for tag in test_case['Tags'].split(',')]
                for tag in tags:
                    robot_test.tags.add(tag)
            try:
                self.create_test_steps(robot_test, test_steps, data_set)
                logging.info(f"{self.__class__.__name__}: E2E test case {test_case['Case ID']} with data set {data_set_index} created successfully")
            except Exception as e:
                logging.error(f"{self.__class__.__name__}: Error creating test case {test_case['Case ID']} with data set {data_set_index}: {str(e)}")
                raise

    def create_test_steps(self, robot_test, test_steps: List[Dict], data_set: Dict):
        for _, step in test_steps.iterrows():
            if step['Run'] == 'Y':
                page_name = step['Page Name']
                module_name = step['Module Name']
                parameters = self.extract_parameters(data_set, step['Parameter Name'])

                try:
                    logging.info(f"{self.__class__.__name__}: Creating web step: {page_name}.{module_name}")
                    robot_test.body.create_keyword(name='execute_module', args=[page_name, module_name, parameters])
                except Exception as e:
                    logging.error(f"{self.__class__.__name__}: Error Creating web step {page_name}.{module_name}: {str(e)}")
                    raise

    @staticmethod
    def extract_parameters(data_set: Dict, parameter_names: str) -> Dict:
        parameters = {}
        if parameter_names != '':
            for name in parameter_names.split(','):
                if name in data_set:
                    value = data_set[name]
                    # Add type conversion here if needed
                    parameters[name] = value
                else:
                    logging.warning(f"WebUIRobotCasesGenerator: Parameter {name} not found in data set")
            logging.info(f"WebUIRobotCasesGenerator: Extracted parameters: {parameters}")
        return parameters
