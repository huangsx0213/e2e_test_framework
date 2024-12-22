import logging
import os
import json
import time
from typing import Dict, Tuple

import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
import base64
from selenium.webdriver.common.by import By

from libraries.common.utility_helpers import PROJECT_ROOT
from libraries.common.config_manager import ConfigManager
from libraries.performance.web_pt_loader import PerformanceTestLoader
from libraries.web.webdriver_factory import WebDriverFactory
from libraries.web.web_actions import WebElementActions

class WebPerformanceTester:
    def __init__(self, test_config_path: str = None, test_cases_path: str = None):
        self.project_root = PROJECT_ROOT
        self.test_config_path = test_config_path or os.path.join(self.project_root, 'configs', 'web_test_config.yaml')
        self.test_cases_path = test_cases_path or os.path.join(self.project_root, 'test_cases', 'web_pt_cases.xlsx')

        self._web_actions_instance = None
        self._driver = None
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
            'Rounds': env_config['Rounds']
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

    def execute_tests(self):
        rounds = int(self.main_config['Rounds'])
        target_url = self.main_config['Target URL']

        for _, test_case in self.test_cases.iterrows():
            if test_case['Run'] == 'Y':
                case_id = test_case['Case ID']
                case_functions = self.test_functions[self.test_functions['Case ID'] == case_id].sort_values('Execution Order')

                for _ in range(rounds):
                    self.driver.get(target_url)
                    memory_usage = self.get_js_memory()
                    if memory_usage is not None:
                        self.memory_usage_data.append({"case_id": case_id, "used_MB": memory_usage})

                    for _, function in case_functions.iterrows():
                        function_name = function['Function Name']
                        self._execute_test_function(function_name, case_id)

    def _execute_test_function(self, function_name, case_id):
        function_steps = self.test_functions[self.test_functions['Function Name'] == function_name].iloc[0]

        precondition_steps = self.sub_functions[self.sub_functions['Sub Function Name'] == function_steps['Precondition subFunction']].sort_values('Step Order')
        operation_steps = self.sub_functions[self.sub_functions['Sub Function Name'] == function_steps['Operation subFunction']].sort_values('Step Order')
        postcondition_steps = self.sub_functions[self.sub_functions['Sub Function Name'] == function_steps['Postcondition subFunction']].sort_values('Step Order')

        # Execute precondition steps
        for _, step in precondition_steps.iterrows():
            self._execute_step(step)

        # Execute operation steps and measure response time
        for _, step in operation_steps.iterrows():
            start_time = time.time()
            self._execute_step(step)
            end_time = time.time()
            response_time = round(end_time - start_time, 2)
            self.response_time_data.append({
                "case_id": case_id,
                "function_name": function_name,
                "response_time": response_time
            })

        # Execute postcondition steps
        for _, step in postcondition_steps.iterrows():
            self._execute_step(step)

    def _execute_step(self, step):
        action_name = step['Action'].lower()
        page = step['Page']
        element = step['Element']
        input_value = step['Input Value (if applicable)']
        locator = self.page_elements[page][element] if element else None

        if hasattr(self.web_actions, action_name):
            action = getattr(self.web_actions, action_name)
            action(locator, input_value) if locator else action(input_value)
        else:
            raise ValueError(f"Unknown action type: {step['Action']}")

    def _load_page_elements(self) -> Dict[str, Dict[str, Tuple[str, str]]]:
        elements = {}
        for _, row in self.locators.iterrows():
            elements.setdefault(row['Page'], {})[row['Element']] = (row['Locator Type'], row['Locator Value'])
        return elements

    def generate_memory_usage_chart(self):
        df = pd.DataFrame(self.memory_usage_data)
        plt.figure(figsize=(10, 6))
        plt.plot(df["case_id"], df["used_MB"], marker="o", label="Used Memory (MB)", color="blue")
        plt.title("JavaScript Memory Usage Trend")
        plt.xlabel("Case ID")
        plt.ylabel("Memory (MB)")
        plt.grid()
        plt.legend()
        return self._save_fig_as_base64()

    def generate_response_time_statistics_chart(self):
        df = pd.DataFrame(self.response_time_data)
        stats = df.groupby("function_name").agg({"response_time": ["mean", "max"]})
        stats.columns = ["Mean", "Max"]
        stats.reset_index(inplace=True)

        stats.plot(kind="bar", x="function_name", figsize=(10, 6), colormap="coolwarm")
        plt.title("Response Time Statistics")
        plt.xlabel("Function Name")
        plt.ylabel("Time (s)")
        plt.grid(axis="y")
        plt.xticks(rotation=45)
        return self._save_fig_as_base64()

    def generate_response_time_trend_chart(self):
        df = pd.DataFrame(self.response_time_data)
        plt.figure(figsize=(10, 6))
        for func in df["function_name"].unique():
            func_data = df[df["function_name"] == func]
            plt.plot(func_data["case_id"], func_data["response_time"], marker="o", label=func)

        plt.title("Response Time Trend")
        plt.xlabel("Case ID")
        plt.ylabel("Response Time (s)")
        plt.legend(title="Function Names")
        plt.grid()
        return self._save_fig_as_base64()

    def generate_response_time_statistics_table(self):
        df = pd.DataFrame(self.response_time_data)
        stats = df.groupby("function_name").agg({
            "response_time": [
                lambda x: round(x.mean(), 2),
                lambda x: round(x.max(), 2),
                lambda x: round(x.min(), 2),
                lambda x: round(x.median(), 2),
                lambda x: round(x.quantile(0.9), 2),
                lambda x: round(x.quantile(0.95), 2),
                lambda x: round(x.quantile(0.99), 2)
            ]
        }).reset_index()

        stats.columns = ["Function Name", "Mean (s)", "Max (s)", "Min (s)",
                         "Median (s)", "P90 (s)", "P95 (s)", "P99 (s)"]

        fig, ax = plt.subplots(figsize=(10, len(stats) * 0.8))
        ax.axis("tight")
        ax.axis("off")
        table = plt.table(cellText=stats.values, colLabels=stats.columns, cellLoc="center", loc="center")
        table.auto_set_font_size(False)
        table.set_fontsize(8)
        return self._save_fig_as_base64()

    def save_to_csv(self):
        if self.response_time_data:
            response_time_df = pd.DataFrame(self.response_time_data)
            response_time_df.to_csv("response_time_data.csv", index=False)
            logging.info("Response time data saved to 'response_time_data.csv'.")

        if self.memory_usage_data:
            memory_usage_df = pd.DataFrame(self.memory_usage_data)
            memory_usage_df.to_csv("memory_usage_data.csv", index=False)
            logging.info("Memory usage data saved to 'memory_usage_data.csv'.")

    def _save_fig_as_base64(self):
        buf = BytesIO()
        plt.savefig(buf, format="png", bbox_inches="tight")
        buf.seek(0)
        base64_image = base64.b64encode(buf.getvalue()).decode("utf-8")
        plt.close()
        return base64_image

    def generate_reports(self):
        # Assuming the reporting configuration is not part of the new Excel structure
        # You can add logic here to generate reports based on your needs
        pass

    def close(self):
        if self._driver:
            self._driver.quit()
            self._driver = None
