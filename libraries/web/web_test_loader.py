import json
import logging
import pandas as pd
import os
from typing import Dict, List
from robot.libraries.BuiltIn import BuiltIn

class WebTestLoader:
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
        sheets = ['Locators', 'PageModules', 'TestCases', 'TestSteps', 'TestData', 'WebEnvironments', 'CustomActions', 'EnvVariables', 'DBConfigs']
        return {sheet: pd.read_excel(self.excel_path, sheet_name=sheet).fillna("") for sheet in sheets}

    def _validate_data(self):
        self._validate_test_cases()
        self._validate_test_steps()
        self._validate_page_objects()
        self._validate_test_data()
        self._validate_web_environments()
        self._validate_custom_actions()
        self._validate_environments()
        self._validate_db_configs()

    def _validate_db_configs(self):
        db_configs = self.get_data_by_sheet_name('DBConfigs')
        required_columns = ['Environment', 'DatabaseName', 'Type', 'User', 'Password', 'Host', 'Port', 'Database', 'Schema', 'ServiceName', 'MinConnections', 'MaxConnections']
        missing_columns = set(required_columns) - set(db_configs.columns)
        if missing_columns:
            logging.error(f"WebTestLoader: Missing required columns in DBConfigs sheet: {', '.join(missing_columns)}")
            raise ValueError(f"WebTestLoader: Missing required columns in DBConfigs sheet: {', '.join(missing_columns)}")

        for index, row in db_configs.iterrows():
            if pd.isna(row['Environment']) or row['Environment'] == '':
                logging.error(f"WebTestLoader: Empty Environment in DBConfigs row {index + 2}")
            if pd.isna(row['DatabaseName']) or row['DatabaseName'] == '':
                logging.error(f"WebTestLoader: Empty DatabaseName in DBConfigs row {index + 2}")
            if row['Type'].lower() not in ['postgresql', 'mysql', 'oracle']:
                logging.error(f"WebTestLoader: Invalid database type '{row['Type']}' in DBConfigs row {index + 2}")

    def get_db_configs(self, environment: str) -> Dict[str, Dict]:
        """获取指定环境的数据库配置"""
        db_configs = self.get_data_by_sheet_name('DBConfigs')
        env_configs = db_configs[db_configs['Environment'] == environment]
        if env_configs.empty:
            logging.error(f"WebTestLoader: No database configurations found for environment: {environment}")
            return {}

        configs = {}
        for _, row in env_configs.iterrows():
            config = {
                'type': row['Type'],
                'user': row['User'],
                'password': row['Password'],
                'host': row['Host'],
                'port': int(row['Port']),
            }

            if row['Type'].lower() in ['postgresql', 'mysql']:
                config.update({
                    'database': row['Database'],
                    'schema': row['Schema'],
                })
            elif row['Type'].lower() == 'oracle':
                config.update({
                    'service_name': row['ServiceName'],
                    'min_connections': int(row['MinConnections']) if pd.notna(row['MinConnections']) else None,
                    'max_connections': int(row['MaxConnections']) if pd.notna(row['MaxConnections']) else None,
                })

            configs[row['DatabaseName']] = config

        return configs

    def _validate_environments(self):
        environments = self.get_data_by_sheet_name('EnvVariables')
        required_columns = ['Environment', 'Variable Name', 'Variable Value']
        missing_columns = set(required_columns) - set(environments.columns)
        if missing_columns:
            logging.error(f"WebTestLoader: Missing required columns in Environments sheet: {', '.join(missing_columns)}")
            raise ValueError(f"WebTestLoader: Missing required columns in Environments sheet: {', '.join(missing_columns)}")

    def _validate_test_cases(self):
        test_cases = self.get_data_by_sheet_name('TestCases')
        test_steps = self.get_data_by_sheet_name('TestSteps')

        case_ids_in_steps = set(test_steps['Case ID'].unique())
        for _, row in test_cases.iterrows():
            case_id = row['Case ID']
            if case_id not in case_ids_in_steps:
                logging.error(f"WebTestLoader: Case ID '{case_id}' does not have any steps defined in the TestSteps sheet.")

    def _validate_test_steps(self):
        test_steps = self.get_data_by_sheet_name('TestSteps')
        page_modules = self.get_data_by_sheet_name('PageModules')

        page_module_combinations = set(zip(page_modules[page_modules['Run'] == 'Y']['Page Name'],
                                           page_modules[page_modules['Run'] == 'Y']['Module Name']))
        for _, row in test_steps[test_steps['Run'] == 'Y'].iterrows():
            if (row['Page Name'], row['Module Name']) not in page_module_combinations and row['Module Name'] != 'API':
                logging.error(
                    f"WebTestLoader: Invalid Page Name '{row['Page Name']}' and Module Name '{row['Module Name']}' combination in TestSteps for Case ID '{row['Case ID']}'.")
            self._validate_parameters(row)

    def _validate_parameters(self, step_row):
        page_modules = self.get_data_by_sheet_name('PageModules')
        test_data = self.get_data_by_sheet_name('TestData')

        module_params = page_modules[(page_modules['Page Name'] == step_row['Page Name']) &
                                     (page_modules['Module Name'] == step_row['Module Name'])]['Parameter Name'].tolist()
        module_params = [param for param in module_params if param]

        if module_params:
            expected_params = set()
            for param in module_params:
                expected_params.update(param.split(','))

            case_data = test_data[test_data['Case ID'] == step_row['Case ID']]
            for param in expected_params:
                if param not in case_data['Parameter Name'].values:
                    logging.error(f"No data provided for parameter '{param}' in TestData for Case ID '{step_row['Case ID']}'")

    def _validate_page_objects(self):
        page_objects = self.get_data_by_sheet_name('PageModules')
        locators = self.get_data_by_sheet_name('Locators')

        locator_map = set(zip(locators['Page Name'], locators['Element Name']))
        for _, row in page_objects[page_objects['Run'] == 'Y'].iterrows():
            if row['Element Name'] and (row['Page Name'], row['Element Name']) not in locator_map:
                logging.error(f"WebTestLoader: Element '{row['Element Name']}' on page '{row['Page Name']}' not found in Locators sheet.")

    def _validate_test_data(self):
        test_data = self.get_data_by_sheet_name('TestData')
        test_steps = self.get_data_by_sheet_name('TestSteps')

        case_ids_in_steps = set(test_steps['Case ID'].unique())
        for _, row in test_data.iterrows():
            if row['Case ID'] not in case_ids_in_steps:
                logging.error(f"WebTestLoader: Test data for Case ID '{row['Case ID']}' does not have corresponding test steps.")

    def _validate_web_environments(self):
        web_environments = self.get_data_by_sheet_name('WebEnvironments')

        if web_environments.empty:
            logging.error("WebTestLoader: WebEnvironments sheet is empty or does not exist.")
            return

        required_columns = ['Environment', 'Browser', 'IsRemote', 'RemoteURL', 'ChromePath', 'ChromeDriverPath', 'EdgePath', 'EdgeDriverPath', 'BrowserOptions']
        missing_columns = set(required_columns) - set(web_environments.columns)
        if missing_columns:
            logging.error(f"WebTestLoader: Missing required columns in WebEnvironments sheet: {', '.join(missing_columns)}")
            return

        # Check if active_environment exists in WebEnvironments
        active_environment = self.test_config.get('active_environment')
        if active_environment and active_environment not in web_environments['Environment'].values:
            logging.error(f"WebTestLoader: Active environment '{active_environment}' specified in config file does not exist in WebEnvironments sheet.")

        for index, row in web_environments.iterrows():
            if self.test_config.get('active_environment') != row['Environment']:
                continue
            if pd.isna(row['Environment']) or row['Environment'] == '':
                logging.error(f"WebTestLoader: Empty Environment name in row {index + 2}")

            if row['Browser'].lower() not in ['chrome', 'edge']:
                logging.error(f"WebTestLoader: Invalid Browser '{row['Browser']}' in row {index + 2}. Must be 'chrome' or 'edge'.")

            if not isinstance(row['IsRemote'], bool):
                logging.error(f"WebTestLoader: IsRemote must be a boolean value in row {index + 2}")

            if row['IsRemote']:
                if pd.isna(row['RemoteURL']) or row['RemoteURL'] == '':
                    logging.error(f"WebTestLoader: RemoteURL is required when IsRemote is True in row {index + 2}")
            else:
                if row['Browser'].lower() == 'chrome':
                    for path_column in ['ChromePath', 'ChromeDriverPath']:
                        if pd.isna(row[path_column]) or row[path_column] == '':
                            logging.error(f"WebTestLoader: {path_column} is required when IsRemote is False and Browser is Chrome in row {index + 2}")
                        elif not os.path.exists(row[path_column]):
                            logging.warning(f"WebTestLoader: {path_column} '{row[path_column]}' does not exist in row {index + 2}")
                elif row['Browser'].lower() == 'edge':
                    for path_column in ['EdgePath', 'EdgeDriverPath']:
                        if pd.isna(row[path_column]) or row[path_column] == '':
                            logging.error(f"WebTestLoader: {path_column} is required when IsRemote is False and Browser is Edge in row {index + 2}")
                        elif not os.path.exists(row[path_column]):
                            logging.warning(f"WebTestLoader: {path_column} '{row[path_column]}' does not exist in row {index + 2}")

            try:
                if not pd.isna(row['BrowserOptions']) and row['BrowserOptions'] != '':
                    json.loads(row['BrowserOptions'])
            except json.JSONDecodeError:
                logging.error(f"WebTestLoader: Invalid JSON in BrowserOptions in row {index + 2}")

        logging.info("WebTestLoader: WebEnvironments data validation completed.")

    def _validate_custom_actions(self):
        custom_actions = self.get_data_by_sheet_name('CustomActions')
        if custom_actions.empty:
            logging.warning("WebTestLoader: CustomActions sheet is empty.")
            return

        required_columns = ['Action Name', 'Python Code']
        missing_columns = set(required_columns) - set(custom_actions.columns)
        if missing_columns:
            logging.error(f"WebTestLoader: Missing required columns in CustomActions sheet: {', '.join(missing_columns)}")
            return

        for index, row in custom_actions.iterrows():
            if pd.isna(row['Action Name']) or row['Action Name'] == '':
                logging.error(f"WebTestLoader: Empty Action Name in CustomActions row {index + 2}")
            if pd.isna(row['Python Code']) or row['Python Code'] == '':
                logging.error(f"WebTestLoader: Empty Python Code for web_element_actions '{row['Action Name']}' in CustomActions row {index + 2}")

    def get_data_by_sheet_name(self, sheet_name: str) -> pd.DataFrame:
        return self.data.get(sheet_name, pd.DataFrame())

    def filter_cases(self, tcid_list: List[str] = None, tags: List[str] = None) -> pd.DataFrame:
        test_cases = self.get_test_cases()

        if tcid_list:
            test_cases = test_cases[test_cases['Case ID'].isin(tcid_list)]

        if tags:
            test_cases = test_cases[test_cases['Tags'].apply(lambda x: any(tag in str(x).split(',') for tag in tags))]

        if test_cases.empty:
            logging.error("WebTestLoader: No test cases found matching criteria.")
            raise ValueError("No test cases found matching criteria.")

        test_cases = test_cases[test_cases['Run'] == 'Y']

        return test_cases

    def get_test_cases(self) -> pd.DataFrame:
        return self.get_data_by_sheet_name('TestCases')

    def get_test_steps(self, case_id: str) -> pd.DataFrame:
        test_steps = self.get_data_by_sheet_name('TestSteps')
        result = test_steps[(test_steps['Case ID'] == case_id) & (test_steps['Run'] == 'Y')]
        if result.empty:
            logging.warning(f"WebTestLoader: No test steps found for case ID: {case_id}")
        return result

    def get_test_data(self, case_id: str) -> List[Dict]:
        test_data = self.get_data_by_sheet_name('TestData')
        case_data = test_data[test_data['Case ID'] == case_id]

        test_steps = self.get_test_steps(case_id)
        non_api_steps = test_steps[test_steps['Module Name'] != 'API']

        if case_data.empty and not non_api_steps.empty:
            logging.warning(f"WebTestLoader: No test data found for case ID: {case_id}")

        grouped_data = case_data.groupby('Data Set')

        data_sets = []
        for _, group in grouped_data:
            data_set = {}
            for _, row in group.iterrows():
                value = self._parse_value(row['Value'], row['Data Type'])
                data_set[row['Parameter Name']] = value
            data_sets.append(data_set)

        return data_sets

    def _parse_value(self, value: str, data_type: str):
        if data_type.lower() == 'json':
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                logging.error(f"Invalid JSON string: {value}")
                return value
        elif data_type.lower() == 'integer':
            try:
                return int(value)
            except ValueError:
                logging.error(f"Invalid integer value: {value}")
                return value
        elif data_type.lower() == 'float':
            try:
                return float(value)
            except ValueError:
                logging.error(f"Invalid float value: {value}")
                return value
        elif data_type.lower() == 'boolean':
            return value.lower() in ('true', 'yes', '1', 'on')
        else:
            return value

    def get_page_objects(self) -> pd.DataFrame:
        page_objects = self.get_data_by_sheet_name('PageModules')
        return page_objects[page_objects['Run'] == 'Y']

    def get_locators(self) -> pd.DataFrame:
        return self.get_data_by_sheet_name('Locators')

    def get_web_environments(self) -> pd.DataFrame:
        return self.get_data_by_sheet_name('WebEnvironments')

    def get_custom_actions(self) -> Dict[str, str]:
        custom_actions_df = self.get_data_by_sheet_name('CustomActions')
        return dict(zip(custom_actions_df['Action Name'], custom_actions_df['Python Code']))

    def get_environments_variables(self) -> List[Dict[str, str]]:
        """获取当前激活环境的所有变量"""
        environments = self.get_data_by_sheet_name('EnvVariables')
        active_env = self.test_config.get('active_environment')
        if not active_env:
            logging.error("WebTestLoader: 'active_environment' is not defined in test_config.")
            return []
        env_vars = environments[environments['Environment'] == active_env]
        if env_vars.empty:
            logging.warning(f"WebTestLoader: No variables found for environment '{active_env}'.")
            return []
        return env_vars.to_dict('records')

    def set_global_variables(self):
        """将环境变量设置为Robot Framework的全局变量"""
        env_variables = self.get_environments_variables()
        built_in = BuiltIn()
        for var in env_variables:
            var_name = var['Variable Name']
            var_value = var['Variable Value']
            built_in.set_global_variable(f"${{{var_name}}}", var_value)
            logging.info(f"WebTestLoader: Set global variable ${{{var_name}}} = {var_value}")
