import pandas as pd


class WebTestLoader:
    def __init__(self, excel_path):
        self.excel_path = excel_path
        self.data = self._load_excel_data()

    def _load_excel_data(self):
        sheets = ['Locators', 'PageModules', 'TestCases', 'TestSteps', 'TestData', 'WebEnvironments']
        return {sheet: pd.read_excel(self.excel_path, sheet_name=sheet).fillna("") for sheet in sheets}

    def get_data(self, sheet_name):
        return self.data.get(sheet_name, pd.DataFrame())

    def get_test_cases(self):
        return self.get_data('TestCases')

    def filter_cases(self, tcid_list=None, tags=None):
        test_cases = self.get_test_cases()

        if tcid_list:
            test_cases = test_cases[test_cases['Case ID'].isin(tcid_list)]

        if tags:
            test_cases = test_cases[test_cases['Tags'].apply(lambda x: any(tag in x for tag in tags))]

        # Filter out the test cases where 'Run' column is not equal to 'Y'
        test_cases = test_cases[test_cases['Run'] == 'Y']

        return test_cases

    def get_test_steps(self, case_id):
        test_steps = self.get_data('TestSteps')
        return test_steps[test_steps['Case ID'] == case_id]

    def get_test_data(self, case_id):
        test_data = self.get_data('TestData')
        case_data = test_data[test_data['Case ID'] == case_id]

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
        return self.get_data('PageModules')

    def get_locators(self):
        return self.get_data('Locators')

    def get_web_environments(self):
        return self.get_data('WebEnvironments')
