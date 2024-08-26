import json
import logging
import os

import pandas as pd


class WebTestLoader:
    def __init__(self, excel_path):
        """
        Initialize the WebTestLoader with the path to the Excel file.
        Load the data and validate it.
        """
        self.excel_path = excel_path
        self.data = self._load_excel_data()
        self._validate_data()

    def _load_excel_data(self):
        """
        Load all relevant sheets from the Excel file into memory.
        Returns a dictionary with sheet names as keys and DataFrames as values.
        """
        sheets = ['Locators', 'PageModules', 'TestCases', 'TestSteps', 'TestData', 'WebEnvironments']
        return {sheet: pd.read_excel(self.excel_path, sheet_name=sheet).fillna("") for sheet in sheets}

    def _validate_data(self):
        """
        Execute all data validation methods to ensure data integrity and consistency.
        """
        self._validate_test_cases()
        self._validate_test_steps()
        self._validate_page_objects()
        self._validate_test_data()

    def _validate_test_cases(self):
        """
        Validate that all test cases have corresponding test steps.
        """
        test_cases = self.get_data_by_sheet_name('TestCases')
        test_steps = self.get_data_by_sheet_name('TestSteps')

        case_ids_in_steps = set(test_steps['Case ID'].unique())
        for _, row in test_cases.iterrows():
            case_id = row['Case ID']
            if case_id not in case_ids_in_steps:
                logging.error(f"WebTestLoader: Case ID '{case_id}' does not have any steps defined in the TestSteps sheet.")

    def _validate_test_steps(self):
        """
        Validate that all Page Name and Module Name combinations in TestSteps exist in PageModules.
        Also validate parameters for each step.
        """
        test_steps = self.get_data_by_sheet_name('TestSteps')
        page_modules = self.get_data_by_sheet_name('PageModules')

        page_module_combinations = set(zip(page_modules['Page Name'], page_modules['Module Name']))
        for _, row in test_steps.iterrows():
            if (row['Page Name'], row['Module Name']) not in page_module_combinations and row['Module Name'] != 'API':
                logging.error(
                    f"WebTestLoader: Invalid Page Name '{row['Page Name']}' and Module Name '{row['Module Name']}' combination in TestSteps for Case ID '{row['Case ID']}'.")
            self._validate_parameters(row)

    def _validate_parameters(self, step_row):
        """
        Validate that parameters in test steps match those defined in PageModules.
        Also check if all parameters have corresponding data in TestData.
        """
        page_modules = self.get_data_by_sheet_name('PageModules')
        test_data = self.get_data_by_sheet_name('TestData')

        module_params = page_modules[(page_modules['Page Name'] == step_row['Page Name']) &
                                     (page_modules['Module Name'] == step_row['Module Name'])]['Parameter Name'].tolist()
        module_params = [param for param in module_params if param]

        if module_params:
            expected_params = set()
            for param in module_params:
                expected_params.update(param.split(','))

            provided_params = set(step_row['Parameter Name'].split(',')) if step_row['Parameter Name'] else set()

            missing_params = expected_params - provided_params
            extra_params = provided_params - expected_params

            if missing_params:
                logging.error(f"Missing parameters {missing_params} in TestSteps for Case ID '{step_row['Case ID']}', Step '{step_row['Step ID']}'")
            if extra_params:
                logging.error(f"Extra parameters {extra_params} in TestSteps for Case ID '{step_row['Case ID']}', Step '{step_row['Step ID']}'")

            case_data = test_data[test_data['Case ID'] == step_row['Case ID']]
            for param in expected_params:
                if param not in case_data['Parameter Name'].values:
                    logging.error(f"No data provided for parameter '{param}' in TestData for Case ID '{step_row['Case ID']}'")

    def _validate_page_objects(self):
        """
        Validate that all Element Names in PageModules have corresponding locators in the Locators sheet.
        """
        page_objects = self.get_data_by_sheet_name('PageModules')
        locators = self.get_data_by_sheet_name('Locators')

        locator_map = set(zip(locators['Page Name'], locators['Element Name']))
        for _, row in page_objects.iterrows():
            if row['Element Name'] and (row['Page Name'], row['Element Name']) not in locator_map:
                logging.error(f"WebTestLoader: Element '{row['Element Name']}' on page '{row['Page Name']}' not found in Locators sheet.")

    def _validate_test_data(self):
        """
        Validate that all Case IDs in TestData have corresponding steps in TestSteps.
        """
        test_data = self.get_data_by_sheet_name('TestData')
        test_steps = self.get_data_by_sheet_name('TestSteps')

        case_ids_in_steps = set(test_steps['Case ID'].unique())
        for _, row in test_data.iterrows():
            if row['Case ID'] not in case_ids_in_steps:
                logging.error(f"WebTestLoader: Test data for Case ID '{row['Case ID']}' does not have corresponding test steps.")

    def get_data_by_sheet_name(self, sheet_name):
        """
        Retrieve data for a specific sheet.
        Returns an empty DataFrame if the sheet doesn't exist.
        """
        return self.data.get(sheet_name, pd.DataFrame())

    def filter_cases(self, tcid_list=None, tags=None):
        """
        Filter test cases based on provided case IDs and tags.
        Only returns cases where 'Run' column is 'Y'.
        """
        test_cases = self.get_test_cases()

        if tcid_list:
            test_cases = test_cases[test_cases['Case ID'].isin(tcid_list)]

        if tags:
            test_cases = test_cases[test_cases['Tags'].apply(lambda x: any(tag in x for tag in tags))]

        test_cases = test_cases[test_cases['Run'] == 'Y']

        return test_cases

    def get_test_cases(self):
        """
        Retrieve all test cases from the TestCases sheet.
        """
        return self.get_data_by_sheet_name('TestCases')

    def get_test_steps(self, case_id):
        """
        Retrieve test steps for a specific case ID.
        Logs a warning if no steps are found.
        """
        test_steps = self.get_data_by_sheet_name('TestSteps')
        result = test_steps[test_steps['Case ID'] == case_id]
        if result.empty:
            logging.warning(f"WebTestLoader: No test steps found for case ID: {case_id}")
        return result

    def get_test_data(self, case_id):
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

    def _parse_value(self, value, data_type):
        if data_type.lower() == 'json':
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                logging.error(f"Invalid JSON string: {value}")
                return value  # 返回原始字符串，以防解析失败
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
            return value  # 默认作为字符串处理

    def get_page_objects(self):
        """
        Retrieve all page objects from the PageModules sheet.
        """
        return self.get_data_by_sheet_name('PageModules')

    def get_locators(self):
        """
        Retrieve all locators from the Locators sheet.
        """
        return self.get_data_by_sheet_name('Locators')

    def get_web_environments(self):
        """
        Retrieve all web environments from the WebEnvironments sheet.
        Perform data integrity and correctness validation.
        """
        web_environments = self.get_data_by_sheet_name('WebEnvironments')

        if web_environments.empty:
            logging.error("WebTestLoader: WebEnvironments sheet is empty or does not exist.")
            return pd.DataFrame()

        required_columns = ['Environment', 'Browser', 'IsRemote', 'RemoteURL', 'ChromePath', 'ChromeDriverPath', 'EdgePath', 'EdgeDriverPath', 'BrowserOptions']
        missing_columns = set(required_columns) - set(web_environments.columns)
        if missing_columns:
            logging.error(f"WebTestLoader: Missing required columns in WebEnvironments sheet: {', '.join(missing_columns)}")
            return pd.DataFrame()

        for index, row in web_environments.iterrows():
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
        return web_environments
