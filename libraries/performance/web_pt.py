import logging
import os
import json
import time
from typing import Dict, Tuple
from libraries.common.utility_helpers import PROJECT_ROOT
from libraries.common.config_manager import ConfigManager
from libraries.performance.web_pt_loader import PerformanceTestLoader
from libraries.web.webdriver_factory import WebDriverFactory
from libraries.web.web_actions import WebElementActions
from libraries.performance.web_pt_reporter import WebPerformanceReporter

class WebPerformanceTester:
    def __init__(self, test_config_path: str = None, test_cases_path: str = None):
        self.project_root = PROJECT_ROOT
        self.test_config_path = test_config_path or os.path.join(self.project_root, 'configs', 'web_pt_config.yaml')
        self.test_cases_path = test_cases_path or os.path.join(self.project_root, 'test_cases', 'web_pt_cases.xlsx')

        self._web_actions_instance = None
        self._driver = None
        self.current_case_id = None
        self.response_time_data = []
        self.memory_usage_data = []

        self._load_configuration()
        self._initialize_components()

    def _load_configuration(self):
        self.test_config = ConfigManager.load_yaml(self.test_config_path)
        self.performance_test_loader = PerformanceTestLoader(self.test_cases_path, self.test_config)
        self.env_config = self._load_environment_config()
        self.main_config = self._load_main_config()

    def _load_main_config(self):
        web_environments = self.performance_test_loader.get_web_environments()
        active_env = self.test_config['active_environment']
        env_config = web_environments[web_environments['Environment'] == active_env].iloc[0].to_dict()
        return {
            'Target URL': env_config['TargetURL'],
            'Rounds': env_config['Rounds'],
            'Log Details': env_config['LogDetails']
        }

    def _load_environment_config(self):
        web_environments = self.performance_test_loader.get_web_environments()
        active_env = self.test_config['active_environment']
        env_config = web_environments[web_environments['Environment'] == active_env].iloc[0].to_dict()
        env_config['BrowserOptions'] = json.loads(env_config['BrowserOptions'])

        return {
            'environments': {
                active_env: {
                    'browser': env_config['Browser'],
                    'is_remote': env_config['IsRemote'],
                    'remote_url': env_config['RemoteURL'],
                    'chrome_path': env_config['ChromePath'],
                    'chrome_driver_path': env_config['ChromeDriverPath'],
                    'edge_path': env_config['EdgePath'],
                    'edge_driver_path': env_config['EdgeDriverPath'],
                    'browser_options': env_config['BrowserOptions']
                }
            }
        }

    def _initialize_components(self):
        self.test_cases = self.performance_test_loader.get_test_cases()
        self.test_functions = self.performance_test_loader.get_test_functions()
        self.sub_functions = self.performance_test_loader.get_sub_functions()
        self.locators = self.performance_test_loader.get_locators()
        self.page_elements = self._load_page_elements()
        self.custom_actions = self.performance_test_loader.get_custom_actions()

    @property
    def driver(self):
        if self._driver is None:
            active_env_config = self.env_config['environments'][self.test_config['active_environment']]
            self._driver = WebDriverFactory.create_driver(active_env_config)
        return self._driver

    @property
    def web_actions(self):
        if self._web_actions_instance is None:
            self._web_actions_instance = WebElementActions(self.driver)
        return self._web_actions_instance

    def get_js_memory(self):
        try:
            js_memory = self.driver.execute_script("return window.performance.memory;")
            if js_memory:
                used_js_memory_mb = js_memory.get("usedJSHeapSize", 0) / (1024 * 1024)
                return round(used_js_memory_mb, 2)
        except Exception as e:
            logging.error(f"Error in get_js_memory: {e}")
        return None

    def execute_single_test(self, case_id: str):
        case_name = self.test_cases[self.test_cases['Case ID'] == case_id]['Name'].iloc[0]
        logging.info(f"Executing test case: {case_id} - {case_name}")


        try:
            rounds = int(self.main_config['Rounds'])
            target_url = self.main_config['Target URL']

            test_case = self.test_cases[self.test_cases['Case ID'] == case_id].iloc[0]
            if test_case['Run'] != 'Y':
                logging.warning(f"Test case {case_id} is not marked to run.")
                return

            case_functions = self.test_functions[self.test_functions['Case ID'] == case_id].sort_values('Execution Order')

            for round_num in range(rounds):
                self.driver.get(target_url)
                memory_usage = self.get_js_memory()
                if memory_usage is not None:
                    self.memory_usage_data.append({"round": round_num + 1, "case_id": case_id, "used_MB": memory_usage})

                for _, function in case_functions.iterrows():
                    function_name = function['Function Name']
                    self._execute_test_function(round_num, function_name, case_id)
        finally:
            logging.info(f"Finished executing test case: {case_id} - {case_name}")

    def _execute_test_function(self, round_num, function_name, case_id):
        function_steps = self.test_functions[self.test_functions['Function Name'] == function_name].iloc[0]

        precondition_steps = self.sub_functions[self.sub_functions['Sub Function Name'] == function_steps['Precondition subFunction']].sort_values('Step Order')
        operation_steps = self.sub_functions[self.sub_functions['Sub Function Name'] == function_steps['Operation subFunction']].sort_values('Step Order')
        postcondition_steps = self.sub_functions[self.sub_functions['Sub Function Name'] == function_steps['Postcondition subFunction']].sort_values('Step Order')

        for _, step in precondition_steps.iterrows():
            self._execute_step(step)
        start_time = time.time()
        for _, step in operation_steps.iterrows():
            self._execute_step(step)
        end_time = time.time()
        response_time = round(end_time - start_time, 2)
        self.response_time_data.append({
            "round": round_num + 1,
            "case_id": case_id,
            "function_name": function_name,
            "response_time": response_time
        })
        for _, step in postcondition_steps.iterrows():
            self._execute_step(step)

    def _execute_step(self, step):
        action_name = step['Action'].lower()
        page = step['Page']
        element = step['Element']
        input_value = step['Input Value (if applicable)']
        locator = self.page_elements[page][element] if element else None

        logging.info(
            f"{self.__class__.__name__}: Executing action:[{action_name}] on page:[{page}]"
            + (f" element:[{element}]" if element else "")
            + (f" with input:[{input_value}]" if input_value else "")
        )
        self.change_log_level = self.main_config['Log Details']
        if self.change_log_level != 'Y':
            # Temporarily set the logging level to WARNING
            logger = logging.getLogger()
            original_level = logger.level
            logger.setLevel(logging.WARNING)

        try:
            if hasattr(self.web_actions, action_name):
                action = getattr(self.web_actions, action_name)
                if locator is not None:
                    if input_value:
                        action(locator, input_value)
                    else:
                        action(locator)
                else:
                    if input_value:
                        action(input_value)
                    else:
                        action()
            else:
                raise ValueError(f"Unknown action type: {step['Action']}")
            logging.info("="*100)
        finally:

            # Restore the original logging level after execution
            if self.change_log_level != 'Y':
                logger.setLevel(original_level)

    def _load_page_elements(self) -> Dict[str, Dict[str, Tuple[str, str]]]:
        elements = {}
        for _, row in self.locators.iterrows():
            elements.setdefault(row['Page'], {})[row['Element']] = (row['Locator Type'], row['Locator Value'])
        return elements

    def generate_reports(self, case_id: str = None):
        if case_id is None:
            case_id = self.current_case_id

        # Get the case name from the test cases
        case_name = self.test_cases[self.test_cases['Case ID'] == case_id]['Name'].iloc[0]

        filtered_response_time_data = [data for data in self.response_time_data if data['case_id'] == case_id]
        filtered_memory_usage_data = [data for data in self.memory_usage_data if data['case_id'] == case_id]

        reporter = WebPerformanceReporter(filtered_response_time_data, filtered_memory_usage_data)

        return {
            'memory_chart': reporter.generate_memory_usage_chart(case_id, case_name),
            'response_time_stats_chart': reporter.generate_response_time_statistics_chart(case_id, case_name),
            'response_time_trend_chart': reporter.generate_response_time_trend_chart(case_id, case_name),
            'response_time_table': reporter.generate_response_time_statistics_table(case_id, case_name)
        }

    def save_to_csv(self):
        reporter = WebPerformanceReporter(self.response_time_data, self.memory_usage_data)
        reporter.save_to_csv()

    def close(self):
        if self._driver:
            self._driver.quit()
            self._driver = None