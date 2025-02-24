import os
import logging
from typing import Dict, List
import pandas as pd
from robot.api import TestSuite
from libraries.common.config_manager import ConfigManager
from libraries.common.utility_helpers import PROJECT_ROOT
from libraries.api.api_test_loader import APITestLoader
from libraries.robot.case_generator.base_generator import RobotCaseGenerator

class APIRobotCaseGenerator(RobotCaseGenerator):
    def __init__(self, test_config_path: str = None, test_cases_path: str = None):
        self.project_root: str = PROJECT_ROOT
        self.test_config_path = test_config_path
        self.test_cases_path = test_cases_path
        self.test_config = None
        self.api_test_loader = None
        self.api_suite = None

    def load_configuration(self):
        self.test_config_path = self.test_config_path or os.path.join(self.project_root, 'configs', 'api_test_config.yaml')
        try:
            self.test_config: Dict = ConfigManager.load_yaml(self.test_config_path)
            logging.info(f"{self.__class__.__name__}: Configuration loaded successfully from {self.test_config_path}")
        except Exception as e:
            logging.error(f"{self.__class__.__name__}: Error loading configuration: {str(e)}")
            raise

    def initialize_components(self):
        default_test_cases_path: str = os.path.join('test_cases', 'api_test_cases.xlsx')
        self.test_cases_path = (
            os.path.join(self.project_root, self.test_config.get('test_cases_path', default_test_cases_path))
            if self.test_cases_path is None
            else self.test_cases_path
        )

        if not os.path.exists(self.test_cases_path):
            logging.error(f"{self.__class__.__name__}: Test cases file not found at {self.test_cases_path}")
            raise FileNotFoundError(f"{self.__class__.__name__}: Test cases file does not exist: {self.test_cases_path}")

        self.api_test_loader = APITestLoader(self.test_cases_path)
        logging.info(f"{self.__class__.__name__}: Components initialized successfully")

    def create_test_suite(self, tc_id_list: List[str] = None, tags: List[str] = None, parent_suite=None) -> TestSuite:
        self.api_suite = parent_suite or TestSuite('API TestSuite')
        self.api_suite.teardown.config(name='suite_teardown', args=[])

        self._configure_test_resources(self.api_suite)

        tc_id_list = tc_id_list or self.test_config.get('tc_id_list', [])
        tags = tags or self.test_config.get('tags', [])

        filtered_cases = self._filter_cases(tc_id_list, tags)

        self._create_test_cases(filtered_cases)

        logging.info(f"{self.__class__.__name__}: Test suite created successfully")
        return self.api_suite

    def create_test_case(self, suite, test_case):
        try:
            robot_api_test_name = f"{test_case['TCID']}"
            robot_api_test = suite.tests.create(
                name=robot_api_test_name,
                doc=test_case['Descriptions']
            )
            robot_api_test.body.create_keyword(name='api_sanity_check', args=[])
            self._add_test_tags(robot_api_test, test_case)
            robot_api_test.body.create_keyword(name='execute_api_test_case', args=[test_case['TCID']])
            self._configure_test_conditions(suite, robot_api_test, test_case)
            logging.info(f"{self.__class__.__name__}: Test case {test_case['TCID']} created successfully")
        except Exception as e:
            logging.error(f"{self.__class__.__name__}: Error creating test case {test_case.get('TCID', 'Unknown')}: {str(e)}")
            raise

    def create_test_steps(self, robot_test, test_steps, data_set):
        # API tests don't have specific steps like Web or E2E tests
        pass

    def _filter_cases(self, tc_id_list: List[str], tags: List[str]) -> pd.DataFrame:
        try:
            return self.api_test_loader.filter_cases(tcid_list=tc_id_list, tags=tags)
        except Exception as e:
            logging.error(f"{self.__class__.__name__}: Failed to filter test cases: {str(e)}")
            raise

    def _create_test_cases(self, filtered_cases: pd.DataFrame) -> None:
        try:
            for index, row in filtered_cases.iterrows():
                suite_name = row['Suite']
                if suite_name not in [suite.name for suite in self.api_suite.suites]:
                    suite = self.api_suite.suites.create(name=suite_name)
                    self._configure_test_resources(suite)
                self.create_test_case(suite, row)
        except Exception as e:
            logging.error(f"{self.__class__.__name__}: Error creating test cases: {str(e)}")
            raise

    def _configure_test_resources(self, suite) -> None:
        test_cases_path_arg = os.path.normpath(self.test_cases_path).replace(os.path.sep, '/')
        suite.resource.imports.library(
            'libraries.api.api_test_keywords.APITestKeywords',
            args=[None, test_cases_path_arg]
        )

    def _add_test_tags(self, robot_api_test, test_case) -> None:
        try:
            if 'Tags' in test_case and pd.notna(test_case['Tags']):
                tags = [tag.strip() for tag in test_case['Tags'].split(',')]
                for tag in tags:
                    robot_api_test.tags.add(tag)
        except Exception as e:
            logging.error(f"{self.__class__.__name__}: Error adding tags to test case: {str(e)}")
            raise

    def _configure_test_conditions(self, suite, robot_api_test, test_case) -> None:
        try:
            if pd.notna(test_case['Conditions']):
                conditions = test_case['Conditions'].splitlines()
                for condition in conditions:
                    self._process_condition(condition, suite, robot_api_test)
        except Exception as e:
            logging.error(f"{self.__class__.__name__}: Error configuring test conditions: {str(e)}")
            raise

    def _process_condition(self, condition: str, suite, robot_api_test) -> None:
        try:
            condition_mapping = {
                '[TestSetup]': (robot_api_test.setup, 'Test setup'),
                '[TestTeardown]': (robot_api_test.teardown, 'Test teardown'),
                '[SuiteSetup]': (suite.setup, 'Suite setup'),
                '[SuiteTeardown]': (suite.teardown, 'Suite teardown')
            }

            for condition_type, (config_object, condition_name) in condition_mapping.items():
                if condition_type in condition:
                    case_ids = condition.strip(condition_type).split(',')
                    config_object.config(
                        name='execute_conditions_cases',
                        args=[case_ids]
                    )
                    logging.info(f"{self.__class__.__name__}: Configured {condition_name} with case IDs: {case_ids}")
        except Exception as e:
            logging.error(f"{self.__class__.__name__}: Error processing condition '{condition}': {str(e)}")
            raise