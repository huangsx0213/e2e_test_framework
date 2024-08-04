import pandas as pd


class APITestLoader:
    def __init__(self, excel_path):
        self.excel_path = excel_path
        self.data = self._load_excel_data()

    def _load_excel_data(self):
        sheets = ['API', 'Headers', 'BodyTemplates', 'BodyDefaults']
        return {sheet: pd.read_excel(self.excel_path, sheet_name=sheet).fillna("") for sheet in sheets}

    def get_data(self, sheet_name):
        return self.data.get(sheet_name, pd.DataFrame())

    def get_api_test_cases(self):
        return self.get_data('API')

    def filter_cases(self, tcid_list=None, tags=None):
        test_cases = self.get_api_test_cases()

        if tcid_list:
            test_cases = test_cases[test_cases['TCID'].isin(tcid_list)]

        if tags:
            test_cases = test_cases[test_cases['Tags'].apply(lambda x: any(tag in x for tag in tags))]

        # Filter out the test cases where 'Run' column is not equal to 'Y'
        test_cases = test_cases[test_cases['Run'] == 'Y']

        return test_cases

    def get_headers(self):
        return self.get_data('Headers')

    def get_body_templates(self):
        return self.get_data('BodyTemplates')

    def get_body_defaults(self):
        return self.get_data('BodyDefaults')
