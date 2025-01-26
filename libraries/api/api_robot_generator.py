import logging
import os
from typing import Dict, List, Any
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
        self.test_cases_df = None
        self.api_suite = None

        self._initialize()

    def _initialize(self) -> None:
        """Initialize the configuration and components."""
        self._load_configuration()
        self._initialize_components()

    def _load_configuration(self) -> None:
        """Load configuration from YAML file."""
        self.test_config_path = self.test_config_path or os.path.join(self.project_root, 'configs', 'api_test_config.yaml')

        try:
            self.test_config: Dict = ConfigManager.load_yaml(self.test_config_path)
            logging.info(f"{self.__class__.__name__}: Configuration loaded successfully from {self.test_config_path}")
        except FileNotFoundError:
            logging.error(f"{self.__class__.__name__}: Config file not found at {self.test_config_path}")
            raise
        except Exception as e:
            logging.error(f"{self.__class__.__name__}: Error loading configuration: {str(e)}")
            raise

    def _initialize_components(self) -> None:
        """Initialize components required for test case generation."""
        default_test_cases_path: str = os.path.join('test_cases', 'api_test_cases.xlsx')
        self.test_cases_path = (
            os.path.join(self.project_root, self.test_config.get('test_cases_path', default_test_cases_path))
            if self.test_cases_path is None
            else self.test_cases_path
        )

        if not os.path.exists(self.test_cases_path):
            logging.error(f"{self.__class__.__name__}: Test cases file not found at {self.test_cases_path}")
            raise FileNotFoundError(f"{self.__class__.__name__}: Test cases file does not exist: {self.test_cases_path}")
        logging.info(f"{self.__class__.__name__}: Test cases file {self.test_cases_path} located successfully")
        self.test_cases_df = APITestLoader(self.test_cases_path)
        logging.info(f"{self.__class__.__name__}: Components initialized successfully")

    def create_test_suite(self, tc_id_list: List[str] = None, tags: List[str] = None, test_suite=None) -> TestSuite:
        self.api_suite = test_suite if test_suite else TestSuite('API TestSuite')
        self.api_suite.teardown.config(name='suite_teardown', args=[])

        self._configure_test_resources(self.api_suite)

        tc_id_list = tc_id_list or self.test_config.get('tc_id_list', [])
        tags = tags or self.test_config.get('tags', [])

        filtered_cases = self._filter_cases(tc_id_list, tags)

        self._create_test_cases(filtered_cases)

        logging.info(f"{self.__class__.__name__}: Test suite created successfully")
        return self.api_suite

    def _filter_cases(self, tc_id_list: List[str], tags: List[str]) -> pd.DataFrame:
        """Filter test cases based on the provided TC ID list and tags."""
        try:
            return self.test_cases_df.filter_cases(tcid_list=tc_id_list, tags=tags)
        except Exception as e:
            logging.error(f"{self.__class__.__name__}: Failed to filter test cases: {str(e)}")
            raise

    def _create_test_cases(self, filtered_cases: pd.DataFrame) -> None:
        """Create test cases in the provided test suite."""
        try:
            # Group test cases by suite
            grouped_cases = filtered_cases.groupby('Suite')

            for suite_name, suite_cases in grouped_cases:
                suite = self.api_suite.suites.create(name=suite_name)
                self._configure_test_resources(suite)
                for _, test_case in suite_cases.iterrows():
                    self._create_single_test_case(test_case, suite)
        except Exception as e:
            logging.error(f"{self.__class__.__name__}: Error creating test cases: {str(e)}")
            raise

    def _configure_test_resources(self, suite) -> None:
        """Configure the test resources for the test suite."""
        test_cases_path_arg = os.path.normpath(self.test_cases_path).replace(os.path.sep, '/')
        suite.resource.imports.library(
            'libraries.api.api_test_keywords.APITestKeywords',
            args=[None, test_cases_path_arg]
        )

    def _create_single_test_case(self, test_case: pd.Series, suite: TestSuite) -> None:
        """Create a single test case in the test suite."""
        try:
            robot_api_test_name = f"API.{test_case['TCID']}"
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

    def _add_test_tags(self, robot_api_test, test_case) -> None:
        """Add tags to the test case."""
        try:
            if 'Tags' in test_case and pd.notna(test_case['Tags']):
                tags = [tag.strip() for tag in test_case['Tags'].split(',')]
                for tag in tags:
                    robot_api_test.tags.add(tag)
        except Exception as e:
            logging.error(f"{self.__class__.__name__}: Error adding tags to test case: {str(e)}")
            raise

    def _configure_test_conditions(self,suite, robot_api_test, test_case) -> None:
        try:
            if pd.notna(test_case['Conditions']):
                conditions = test_case['Conditions'].splitlines()
                for condition in conditions:
                    self._process_condition(condition,suite, robot_api_test)
        except Exception as e:
            logging.error(f"{self.__class__.__name__}: Error configuring test conditions: {str(e)}")
            raise

    def _process_condition(self, condition: str,suite, robot_api_test) -> None:
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
