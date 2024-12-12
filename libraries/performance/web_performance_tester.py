import os
import json
import time
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
import base64
from selenium import webdriver
from selenium.webdriver.common.by import By

from libraries.common.utility_helpers import PROJECT_ROOT
from libraries.common.config_manager import ConfigManager
from libraries.web.web_test_loader import WebTestLoader
from libraries.web.webdriver_factory import WebDriverFactory
from libraries.web.web_actions import WebElementActions


class WebPerformanceTester:
    def __init__(self, test_config_path: str = None, test_cases_path: str = None):
        self.project_root = PROJECT_ROOT
        self.test_config_path = test_config_path or os.path.join(self.project_root, 'configs', 'web_test_config.yaml')
        self.test_cases_path = test_cases_path or os.path.join(self.project_root, 'test_cases', 'web_performance_test_cases.xlsx')

        self._web_actions_instance = None
        self._driver = None
        self.rounds = 5  # Default value, can be overridden in config
        self.response_time_data = []
        self.memory_usage_data = []

        self._load_configuration()
        self._initialize_components()

    def _load_configuration(self):
        self.test_config = ConfigManager.load_yaml(self.test_config_path)
        self.web_test_loader = WebTestLoader(self.test_cases_path, self.test_config)
        self.env_config = self._load_environment_config()
        self.main_config = self._load_main_config()
        self.rounds = self.main_config.get('Rounds', self.rounds)
        self.target_url = self.main_config.get('Target URL')

    def _load_main_config(self):
        main_config_df = self.web_test_loader.get_data_by_sheet_name('Main Configuration')
        return dict(zip(main_config_df['Configuration Item'], main_config_df['Value']))

    def _load_environment_config(self):
        environments = self.web_test_loader.get_web_environments()
        active_env = self.main_config['Active Environment']
        env_config = environments[environments['Environment'] == active_env].iloc[0].to_dict()
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
        self.test_functions = self._load_test_functions()
        self.function_details = self._load_function_details()
        self.reporting_config = self._load_reporting_config()

    def _load_test_functions(self):
        return self.web_test_loader.get_data_by_sheet_name('Test Functions')

    def _load_function_details(self):
        return self.web_test_loader.get_data_by_sheet_name('Function Details')

    def _load_reporting_config(self):
        return self.web_test_loader.get_data_by_sheet_name('Reporting Configuration')

    @property
    def driver(self):
        if self._driver is None:
            active_env_config = self.env_config['environments'][self.main_config['Active Environment']]
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
            print(f"Error in get_js_memory: {e}")
        return None

    def execute_tests(self):
        for round_num in range(self.rounds):
            self.driver.get(self.target_url)
            memory_usage = self.get_js_memory()
            if memory_usage is not None:
                self.memory_usage_data.append({"round": round_num + 1, "used_MB": memory_usage})

            for _, test_function in self.test_functions.iterrows():
                if test_function['Run'] == 'Y':
                    start_time = time.time()
                    self._execute_test_function(test_function)
                    end_time = time.time()
                    response_time = round(end_time - start_time, 2)
                    self.response_time_data.append({
                        "round": round_num + 1,
                        "function_point": test_function['Function Name'],
                        "response_time": response_time
                    })

    def _execute_test_function(self, test_function):
        function_details = self.function_details[self.function_details['Function Name'] == test_function['Function Name']]
        for _, step in function_details.iterrows():
            self._execute_step(step)

    def _execute_step(self, step):
        action_name = step['Action Type'].lower()
        if hasattr(self.web_actions, action_name):
            action = getattr(self.web_actions, action_name)
            locator = (getattr(By, step['Locator Type']), step['Locator Value'])
            action(locator, step.get('Input Value'))
        else:
            raise ValueError(f"Unknown action type: {step['Action Type']}")

    def generate_memory_usage_chart(self):
        df = pd.DataFrame(self.memory_usage_data)
        plt.figure(figsize=(10, 6))
        plt.plot(df["round"], df["used_MB"], marker="o", label="Used Memory (MB)", color="blue")
        plt.title("JavaScript Memory Usage Trend")
        plt.xlabel("Round")
        plt.ylabel("Memory (MB)")
        plt.grid()
        plt.legend()
        return self._save_fig_as_base64()

    def generate_response_time_statistics_chart(self):
        df = pd.DataFrame(self.response_time_data)
        stats = df.groupby("function_point").agg({"response_time": ["mean", "max"]})
        stats.columns = ["Mean", "Max"]
        stats.reset_index(inplace=True)

        stats.plot(kind="bar", x="function_point", figsize=(10, 6), colormap="coolwarm")
        plt.title("Response Time Statistics")
        plt.xlabel("Function Point")
        plt.ylabel("Time (s)")
        plt.grid(axis="y")
        plt.xticks(rotation=45)
        return self._save_fig_as_base64()

    def generate_response_time_trend_chart(self):
        df = pd.DataFrame(self.response_time_data)
        plt.figure(figsize=(10, 6))
        for func in df["function_point"].unique():
            func_data = df[df["function_point"] == func]
            plt.plot(func_data["round"], func_data["response_time"], marker="o", label=func)

        plt.title("Response Time Trend")
        plt.xlabel("Round")
        plt.ylabel("Response Time (s)")
        plt.legend(title="Function Points")
        plt.grid()
        return self._save_fig_as_base64()

    def generate_response_time_statistics_table(self):
        df = pd.DataFrame(self.response_time_data)
        stats = df.groupby("function_point").agg({
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

        stats.columns = ["Function Point", "Mean (s)", "Max (s)", "Min (s)",
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
            print("Response time data saved to 'response_time_data.csv'.")

        if self.memory_usage_data:
            memory_usage_df = pd.DataFrame(self.memory_usage_data)
            memory_usage_df.to_csv("memory_usage_data.csv", index=False)
            print("Memory usage data saved to 'memory_usage_data.csv'.")

    def _save_fig_as_base64(self):
        buf = BytesIO()
        plt.savefig(buf, format="png", bbox_inches="tight")
        buf.seek(0)
        base64_image = base64.b64encode(buf.getvalue()).decode("utf-8")
        plt.close()
        return base64_image

    def generate_reports(self):
        for _, report_config in self.reporting_config.iterrows():
            if report_config['Generate (Yes/No)'] == 'Yes':
                report_type = report_config['Report Type']
                if report_type == 'Memory Usage Trend Chart':
                    chart = self.generate_memory_usage_chart()
                elif report_type == 'Response Time Statistics Chart':
                    chart = self.generate_response_time_statistics_chart()
                elif report_type == 'Response Time Trend Chart':
                    chart = self.generate_response_time_trend_chart()
                elif report_type == 'Response Time Statistics Table':
                    chart = self.generate_response_time_statistics_table()

                print(f'<h2>{report_type}</h2>')
                print(f'<img src="data:image/png;base64,{chart}" alt="{report_type}"/>')

    def close(self):
        if self._driver:
            self._driver.quit()
            self._driver = None