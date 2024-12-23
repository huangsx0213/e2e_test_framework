import json
import logging
import pandas as pd
import os
from typing import Dict, List

class PerformanceTestLoader:
    _instances = {}

    def __new__(cls, excel_path, test_config):
        key = (excel_path, id(test_config))  # Use a tuple of excel_path and test_config id as the key
        if key not in cls._instances:
            instance = super().__new__(cls)
            instance.__init__(excel_path, test_config)
            cls._instances[key] = instance
        return cls._instances[key]

    def __init__(self, excel_path, test_config):
        if hasattr(self, 'initialized'):
            return
        self.excel_path = excel_path
        self.test_config = test_config
        self.data = self._load_excel_data()
        self._validate_data()
        self.initialized = True

    def _load_excel_data(self) -> Dict[str, pd.DataFrame]:
        sheets = [
            'TestCases', 'TestFunctions', 'SubFunctions', 'Locators', 'WebEnvironments', 'CustomActions'
        ]
        return {sheet: pd.read_excel(self.excel_path, sheet_name=sheet).fillna("") for sheet in sheets}

    def _validate_data(self):
        self._validate_test_cases()
        self._validate_test_functions()
        self._validate_sub_functions()
        self._validate_locators()
        self._validate_web_environments()
        self._validate_custom_actions()

    def _validate_test_cases(self):
        test_cases = self.get_data_by_sheet_name('TestCases')
        required_columns = ['Case ID', 'Description', 'Run']
        missing_columns = set(required_columns) - set(test_cases.columns)
        if missing_columns:
            logging.error(f"PerformanceTestLoader: Missing required columns in TestCases sheet: {', '.join(missing_columns)}")

        for index, row in test_cases.iterrows():
            if pd.isna(row['Case ID']) or row['Case ID'] == '':
                logging.error(f"PerformanceTestLoader: Empty Case ID in TestCases row {index + 2}")
            if row['Run'] not in ['Y', 'N']:
                logging.error(f"PerformanceTestLoader: Invalid Run value in TestCases row {index + 2}. Must be 'Y' or 'N'")

    def _validate_test_functions(self):
        test_functions = self.get_data_by_sheet_name('TestFunctions')
        required_columns = ['Case ID', 'Execution Order', 'Function Name', 'Precondition subFunction', 'Operation subFunction', 'Postcondition subFunction', 'Description']
        missing_columns = set(required_columns) - set(test_functions.columns)
        if missing_columns:
            logging.error(f"PerformanceTestLoader: Missing required columns in TestFunctions sheet: {', '.join(missing_columns)}")

        for index, row in test_functions.iterrows():
            if pd.isna(row['Case ID']) or row['Case ID'] == '':
                logging.error(f"PerformanceTestLoader: Empty Case ID in TestFunctions row {index + 2}")
            if pd.isna(row['Function Name']) or row['Function Name'] == '':
                logging.error(f"PerformanceTestLoader: Empty Function Name in TestFunctions row {index + 2}")

    def _validate_sub_functions(self):
        sub_functions = self.get_data_by_sheet_name('SubFunctions')
        required_columns = ['Sub Function Name', 'Step Order', 'Page', 'Element', 'Action', 'Input Value (if applicable)', 'Description']
        missing_columns = set(required_columns) - set(sub_functions.columns)
        if missing_columns:
            logging.error(f"PerformanceTestLoader: Missing required columns in SubFunctions sheet: {', '.join(missing_columns)}")

        for index, row in sub_functions.iterrows():
            if pd.isna(row['Sub Function Name']) or row['Sub Function Name'] == '':
                logging.error(f"PerformanceTestLoader: Empty Sub Function Name in SubFunctions row {index + 2}")

    def _validate_locators(self):
        locators = self.get_data_by_sheet_name('Locators')
        required_columns = ['Page', 'Element', 'Locator Type', 'Locator Value', 'Description']
        missing_columns = set(required_columns) - set(locators.columns)
        if missing_columns:
            logging.error(f"PerformanceTestLoader: Missing required columns in Locators sheet: {', '.join(missing_columns)}")

        for index, row in locators.iterrows():
            if pd.isna(row['Page']) or row['Page'] == '':
                logging.error(f"PerformanceTestLoader: Empty Page in Locators row {index + 2}")
            if pd.isna(row['Element']) or row['Element'] == '':
                logging.error(f"PerformanceTestLoader: Empty Element in Locators row {index + 2}")
            if row['Locator Type'] not in ['id', 'name', 'xpath', 'css', 'class', 'tag', 'link_text', 'partial_link_text']:
                logging.error(f"PerformanceTestLoader: Invalid Locator Type '{row['Locator Type']}' in Locators row {index + 2}")

    def _validate_web_environments(self):
        web_environments = self.get_data_by_sheet_name('WebEnvironments')
        required_columns = ['Environment', 'TargetURL', 'Rounds', 'Browser', 'IsRemote', 'RemoteURL', 'ChromePath', 'ChromeDriverPath', 'EdgePath', 'EdgeDriverPath', 'BrowserOptions']
        missing_columns = set(required_columns) - set(web_environments.columns)
        if missing_columns:
            logging.error(f"PerformanceTestLoader: Missing required columns in WebEnvironments sheet: {', '.join(missing_columns)}")

        for index, row in web_environments.iterrows():
            if pd.isna(row['Environment']) or row['Environment'] == '':
                logging.error(f"PerformanceTestLoader: Empty Environment name in WebEnvironments row {index + 2}")
            if row['Browser'].lower() not in ['chrome', 'edge']:
                logging.error(f"PerformanceTestLoader: Invalid Browser '{row['Browser']}' in WebEnvironments row {index + 2}. Must be 'chrome' or 'edge'.")
            if not isinstance(row['IsRemote'], bool):
                logging.error(f"PerformanceTestLoader: IsRemote must be a boolean value in WebEnvironments row {index + 2}")
            if row['IsRemote']:
                if pd.isna(row['RemoteURL']) or row['RemoteURL'] == '':
                    logging.error(f"PerformanceTestLoader: RemoteURL is required when IsRemote is True in WebEnvironments row {index + 2}")
            else:
                if row['Browser'].lower() == 'chrome':
                    for path_column in ['ChromePath', 'ChromeDriverPath']:
                        if pd.isna(row[path_column]) or row[path_column] == '':
                            logging.error(f"PerformanceTestLoader: {path_column} is required when IsRemote is False and Browser is Chrome in WebEnvironments row {index + 2}")
                        elif not os.path.exists(row[path_column]):
                            logging.warning(f"PerformanceTestLoader: {path_column} '{row[path_column]}' does not exist in WebEnvironments row {index + 2}")
                elif row['Browser'].lower() == 'edge':
                    for path_column in ['EdgePath', 'EdgeDriverPath']:
                        if pd.isna(row[path_column]) or row[path_column] == '':
                            logging.error(f"PerformanceTestLoader: {path_column} is required when IsRemote is False and Browser is Edge in WebEnvironments row {index + 2}")
                        elif not os.path.exists(row[path_column]):
                            logging.warning(f"PerformanceTestLoader: {path_column} '{row[path_column]}' does not exist in WebEnvironments row {index + 2}")

            try:
                if not pd.isna(row['BrowserOptions']) and row['BrowserOptions'] != '':
                    json.loads(row['BrowserOptions'])
            except json.JSONDecodeError:
                logging.error(f"PerformanceTestLoader: Invalid JSON in BrowserOptions in WebEnvironments row {index + 2}")

    def _validate_custom_actions(self):
        custom_actions = self.get_data_by_sheet_name('CustomActions')
        required_columns = ['Action Name', 'Description', 'Python Code']
        missing_columns = set(required_columns) - set(custom_actions.columns)
        if missing_columns:
            logging.error(f"PerformanceTestLoader: Missing required columns in CustomActions sheet: {', '.join(missing_columns)}")

        for index, row in custom_actions.iterrows():
            if pd.isna(row['Action Name']) or row['Action Name'] == '':
                logging.error(f"PerformanceTestLoader: Empty Action Name in CustomActions row {index + 2}")
            if pd.isna(row['Python Code']) or row['Python Code'] == '':
                logging.error(f"PerformanceTestLoader: Empty Python Code for Action '{row['Action Name']}' in CustomActions row {index + 2}")

    def get_data_by_sheet_name(self, sheet_name: str) -> pd.DataFrame:
        return self.data.get(sheet_name, pd.DataFrame())

    def get_test_cases(self) -> pd.DataFrame:
        return self.get_data_by_sheet_name('TestCases')

    def get_test_functions(self) -> pd.DataFrame:
        return self.get_data_by_sheet_name('TestFunctions')

    def get_sub_functions(self) -> pd.DataFrame:
        return self.get_data_by_sheet_name('SubFunctions')

    def get_locators(self) -> pd.DataFrame:
        return self.get_data_by_sheet_name('Locators')

    def get_web_environments(self) -> pd.DataFrame:
        return self.get_data_by_sheet_name('WebEnvironments')

    def get_custom_actions(self) -> pd.DataFrame:
        return self.get_data_by_sheet_name('CustomActions')
