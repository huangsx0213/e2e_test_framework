import pandas as pd


class APITestLoader:
    def __init__(self, excel_path: str):
        self.excel_path = excel_path
        self.data = {}

    def _load_excel_data(self, sheet_name: str) -> pd.DataFrame:
        if sheet_name not in self.data:
            try:
                self.data[sheet_name] = pd.read_excel(self.excel_path, sheet_name=sheet_name).fillna("")
            except ValueError as e:
                raise ValueError(f"{self.__class__.__name__}: Error loading sheet '{sheet_name}': {e}")
        return self.data[sheet_name]

    def get_data(self, sheet_name: str) -> pd.DataFrame:
        return self._load_excel_data(sheet_name)

    def get_api_test_cases(self) -> pd.DataFrame:
        return self.get_data('API')

    def get_body_templates(self) -> pd.DataFrame:
        return self.get_data('BodyTemplates')

    def get_body_defaults(self) -> pd.DataFrame:
        return self.get_data('BodyDefaults')

    def get_headers(self) -> pd.DataFrame:
        return self.get_data('Headers')

    def get_environments(self) -> pd.DataFrame:
        return self.get_data('Endpoints')

    def filter_cases(self, tcid_list: list = None, tags: list = None) -> pd.DataFrame:
        test_cases = self.get_api_test_cases()

        if tcid_list:
            test_cases = test_cases[test_cases['TCID'].isin(tcid_list)]

        if tags:
            test_cases = test_cases[test_cases['Tags'].apply(lambda x: any(tag in x for tag in tags))]

        # Filter out the test cases where 'Run' column is not equal to 'Y'
        return test_cases[test_cases['Run'] == 'Y']

