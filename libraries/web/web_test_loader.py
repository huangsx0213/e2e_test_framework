import logging

import pandas as pd


class WebTestLoader:
    def __init__(self, excel_path):
        self.excel_path = excel_path
        self.data = self._load_excel_data()

    def _load_excel_data(self):
        sheets = ['Locators', 'PageModules', 'TestCases', 'TestSteps', 'TestData', 'WebEnvironments']
        return {sheet: pd.read_excel(self.excel_path, sheet_name=sheet).fillna("") for sheet in sheets}

    def get_data_by_sheet_name(self, sheet_name):
        return self.data.get(sheet_name, pd.DataFrame())

    def filter_cases(self, tcid_list=None, tags=None):
        test_cases = self.get_test_cases()

        if tcid_list:
            test_cases = test_cases[test_cases['Case ID'].isin(tcid_list)]

        if tags:
            test_cases = test_cases[test_cases['Tags'].apply(lambda x: any(tag in x for tag in tags))]

        # Filter out the test cases where 'Run' column is not equal to 'Y'
        test_cases = test_cases[test_cases['Run'] == 'Y']

        return test_cases

    def get_test_cases(self):
        test_cases = self.get_data_by_sheet_name('TestCases')
        test_steps = self.get_data_by_sheet_name('TestSteps')

        # Create a set of unique Case IDs from the TestSteps sheet
        case_ids_in_steps = set(test_steps['Case ID'].unique())

        for _, row in test_cases.iterrows():
            case_id = row['Case ID']
            if case_id not in case_ids_in_steps:
                logging.error(f"WebTestLoader: Case ID '{case_id}' does not have any steps defined in the TestSteps sheet.")

        return test_cases

    def get_test_steps(self, case_id):
        test_steps = self.get_data_by_sheet_name('TestSteps')
        result = test_steps[test_steps['Case ID'] == case_id]
        if result.empty:
            logging.warning(f"WebTestLoader: No test steps found for case ID: {case_id}")
        return result

    def get_test_data(self, case_id):
        test_data = self.get_data_by_sheet_name('TestData')
        case_data = test_data[test_data['Case ID'] == case_id]

        # Check if there are any test steps for this case
        test_steps = self.get_test_steps(case_id)
        non_api_steps = test_steps[test_steps['Module Name'] != 'API']

        if case_data.empty and not non_api_steps.empty:
            logging.warning(f"WebTestLoader: No test data found for case ID: {case_id}")

        # Group data by 'Data Set' column
        grouped_data = case_data.groupby('Data Set')

        # Create a list of dictionaries, each representing a data set
        data_sets = []
        for _, group in grouped_data:
            data_set = {}
            for _, row in group.iterrows():
                data_set[row['Parameter Name']] = row['Value']
            data_sets.append(data_set)

        return data_sets

    def get_page_objects(self):
        page_objects = self.get_data_by_sheet_name('PageModules')
        locators = self.get_data_by_sheet_name('Locators')

        # Create a dictionary to store the unique (Page Name, Element Name) combinations
        locator_map = {}
        for _, row in locators.iterrows():
            key = (row['Page Name'], row['Element Name'])
            locator_map[key] = (row['Locator Type'], row['Locator Value'])

        for _, row in page_objects.iterrows():
            if row['Element Name'] != '':
                key = (row['Page Name'], row['Element Name'])
                if key not in locator_map:
                    logging.error(f"WebTestLoader: Element '{row['Element Name']}' on page '{row['Page Name']}' not found in Locators sheet.")

        return page_objects

    def get_locators(self):
        return self.get_data_by_sheet_name('Locators')

    def get_web_environments(self):
        return self.get_data_by_sheet_name('WebEnvironments')
