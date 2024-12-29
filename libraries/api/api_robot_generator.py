import logging
import os
from typing import Dict, List
import pandas as pd
from libraries.api.api_test_loader import APITestLoader
from libraries.common.config_manager import ConfigManager
from libraries.common.utility_helpers import PROJECT_ROOT
from robot.api import TestSuite
from libraries.common.log_manager import logger_instance

class APIRobotCasesGenerator:
    def __init__(self, test_config_path: str = None, test_cases_path: str = None) -> None:
        self.project_root: str = PROJECT_ROOT
        self.test_config_path = test_config_path
        self.test_cases_path = test_cases_path

        try:
            self._load_configuration()
            self._initialize_components()
        except Exception as e:
            logging.error(f"{self.__class__.__name__}: Initialization failed: {str(e)}")
            raise RuntimeError(f"{self.__class__.__name__}: Initialization failed: {str(e)}")

    def _load_configuration(self):
        try:
            self.test_config_path = (
                os.path.join(self.project_root, 'configs', 'api_test_config.yaml')
                if self.test_config_path is None
                else self.test_config_path
            )
            self.test_config: Dict = ConfigManager.load_yaml(self.test_config_path)
            logging.info(f"{self.__class__.__name__}: Configuration loaded successfully from {self.test_config_path}")
        except FileNotFoundError:
            logging.error(f"{self.__class__.__name__}: Config file not found at {self.test_config_path}")
            raise
        except Exception as e:
            logging.error(f"{self.__class__.__name__}: Error loading configuration: {str(e)}")
            raise

    def _initialize_components(self):
        try:
            default_test_cases_path: str = os.path.join('test_cases', 'api_test_cases.xlsx')
            self.test_cases_path: str = (
                os.path.join(self.project_root, self.test_config.get('test_cases_path', default_test_cases_path))
                if self.test_cases_path is None
                else self.test_cases_path
            )

            if not os.path.exists(self.test_cases_path):
                logging.error(f"{self.__class__.__name__}: Test cases file not found at {self.test_cases_path}")
                raise FileNotFoundError(f"Test cases file does not exist: {self.test_cases_path}")

            self.test_cases_df = APITestLoader(self.test_cases_path)
            logging.info(f"{self.__class__.__name__}: Components initialized successfully")
        except Exception as e:
            logging.error(f"{self.__class__.__name__}: Error initializing components: {str(e)}")
            raise

    def create_test_suite(self, tc_id_list: List[str] = None, tags: List[str] = None, test_suite=None) -> TestSuite:
        try:
            self.api_suite = test_suite if test_suite else TestSuite('API TestSuite')
            self.api_suite.teardown.config(name='clear_saved_fields', args=[])
            self._configure_test_resources()
            tc_id_list = tc_id_list or self.test_config.get('tc_id_list', [])
            tags = tags or self.test_config.get('tags', [])

            try:
                filtered_cases = self.test_cases_df.filter_cases(tcid_list=tc_id_list, tags=tags)
                self._create_test_cases(filtered_cases)
            except Exception as e:
                logging.error(f"{self.__class__.__name__}: Failed to create test cases: {str(e)}")
                raise

            logging.info(f"{self.__class__.__name__}: Test suite created successfully")
            return self.api_suite

        except Exception as e:
            logging.error(f"{self.__class__.__name__}: Error creating test suite: {str(e)}")
            raise RuntimeError(f"Failed to create test suite: {str(e)}")

    def _configure_test_resources(self):
        try:
            test_cases_path_arg = os.path.normpath(self.test_cases_path).replace(os.path.sep, '/')
            logging.info(f"{self.__class__.__name__}: Using test cases from {test_cases_path_arg}")
            self.api_suite.resource.imports.library(
                'libraries.api.api_test_keywords.APITestKeywords',
                args=[None, test_cases_path_arg]
            )
        except Exception as e:
            logging.error(f"{self.__class__.__name__}: Error configuring test resources: {str(e)}")
            raise

    def _create_test_cases(self, filtered_cases) -> None:
        try:
            for _, test_case in filtered_cases.iterrows():
                self._create_single_test_case(test_case)
        except Exception as e:
            logging.error(f"{self.__class__.__name__}: Error creating test cases: {str(e)}")
            raise

    def _create_single_test_case(self, test_case) -> None:
        try:
            robot_api_test_name = f"API.{test_case['TCID']}"
            robot_api_test = self.api_suite.tests.create(
                name=robot_api_test_name,
                doc=test_case['Descriptions']
            )
            robot_api_test.body.create_keyword(name='api_sanity_check', args=[])
            self._add_test_tags(robot_api_test, test_case)
            robot_api_test.body.create_keyword(
                name='execute_api_test_case',
                args=[test_case['TCID']]
            )
            self._configure_test_conditions(robot_api_test, test_case)
            logging.info(f"{self.__class__.__name__}: Test case {test_case['TCID']} created successfully")

        except Exception as e:
            logging.error(f"{self.__class__.__name__}: Error creating test case {test_case.get('TCID', 'Unknown')}: {str(e)}")
            raise

    def _add_test_tags(self, robot_api_test, test_case) -> None:
        try:
            if 'Tags' in test_case and pd.notna(test_case['Tags']):
                tags = [tag.strip() for tag in test_case['Tags'].split(',')]
                for tag in tags:
                    robot_api_test.tags.add(tag)
        except Exception as e:
            logging.error(f"{self.__class__.__name__}: Error adding tags to test case: {str(e)}")
            raise

    def _configure_test_conditions(self, robot_api_test, test_case) -> None:
        try:
            if pd.notna(test_case['Conditions']):
                conditions = test_case['Conditions'].splitlines()
                for condition in conditions:
                    self._process_condition(condition, robot_api_test)
        except Exception as e:
            logging.error(f"{self.__class__.__name__}: Error configuring test conditions: {str(e)}")
            raise

    def _process_condition(self, condition: str, robot_api_test) -> None:
        try:
            condition_mapping = {
                '[TestSetup]': (robot_api_test.setup, 'Test setup'),
                '[TestTeardown]': (robot_api_test.teardown, 'Test teardown'),
                '[SuiteSetup]': (self.api_suite.setup, 'Suite setup'),
                '[SuiteTeardown]': (self.api_suite.teardown, 'Suite teardown')
            }

            for condition_type, (config_object, condition_name) in condition_mapping.items():
                if condition_type in condition:
                    case_ids = condition.strip(condition_type).split(',')
                    config_object.config(
                        name='execute_multiple_api_test_cases',
                        args=[case_ids]
                    )
                    logging.info(f"{self.__class__.__name__}: Configured {condition_name} with case IDs: {case_ids}")

        except Exception as e:
            logging.error(f"{self.__class__.__name__}: Error processing condition '{condition}': {str(e)}")
            raise
