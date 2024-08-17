import json
import pandas as pd
import yaml


class APITestLoader:
    def __init__(self, excel_path: str):
        self.excel_path = excel_path
        self.data = {}
        self.validate_excel_structure()

    def _load_excel_data(self, sheet_name: str) -> pd.DataFrame:
        if sheet_name not in self.data:
            try:
                self.data[sheet_name] = pd.read_excel(self.excel_path, sheet_name=sheet_name).fillna('')
                self.validate_sheet_data(sheet_name, self.data[sheet_name])
            except ValueError as e:
                raise ValueError(f"Error loading sheet '{sheet_name}': {e}")
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

    def get_endpoints(self) -> pd.DataFrame:
        return self.get_data('Endpoints')

    def filter_cases(self, tcid_list: list = None, tags: list = None) -> pd.DataFrame:
        test_cases = self.get_api_test_cases()

        if tcid_list:
            test_cases = test_cases[test_cases['TCID'].isin(tcid_list)]

        if tags:
            test_cases = test_cases[test_cases['Tags'].apply(lambda x: any(tag in x for tag in tags))]

        # Filter out the test cases where 'Run' column is not equal to 'Y'
        return test_cases[test_cases['Run'] == 'Y']

    def validate_excel_structure(self):
        required_sheets = ['API', 'BodyTemplates', 'BodyDefaults', 'Headers', 'Endpoints']
        existing_sheets = pd.ExcelFile(self.excel_path).sheet_names
        missing_sheets = set(required_sheets) - set(existing_sheets)
        if missing_sheets:
            raise ValueError(f"Missing required sheets: {', '.join(missing_sheets)}")

    def validate_sheet_data(self, sheet_name: str, df: pd.DataFrame):
        validation_methods = {
            'API': self._validate_api_sheet,
            'BodyTemplates': self._validate_body_templates_sheet,
            'BodyDefaults': self._validate_body_defaults_sheet,
            'Headers': self._validate_headers_sheet,
            'Endpoints': self._validate_endpoints_sheet
        }
        if sheet_name in validation_methods:
            validation_methods[sheet_name](df)

    def _validate_api_sheet(self, df: pd.DataFrame):
        required_columns = ['TCID', 'Name', 'Run', 'Endpoint', 'Body Template', 'Body Default', 'Body User-defined Fields', 'Headers']
        missing_columns = set(required_columns) - set(df.columns)
        if missing_columns:
            raise ValueError(f"Missing required columns in API sheet: {', '.join(missing_columns)}")

        # Check for duplicate TCID
        if df['TCID'].duplicated().any():
            raise ValueError("Duplicate TCID found in API sheet")

        # Ensure 'Run' column has only 'Y' or 'N'
        if not df['Run'].isin(['Y', 'N']).all():
            raise ValueError("Invalid values in 'Run' column. Only 'Y' or 'N' are allowed.")

        # Validate mandatory fields, considering GET and DELETE requests
        for index, row in df.iterrows():
            method = self.get_endpoints().loc[self.get_endpoints()['Endpoint'] == row['Endpoint'], 'Method'].iloc[0]
            if method in ['GET', 'DELETE']:
                # Allow '' for 'Body Template' and 'Body Default'
                fields_to_check = ['TCID', 'Name', 'Endpoint', 'Headers']
            else:
                # Do not allow '' for any mandatory field
                fields_to_check = required_columns

            for field in fields_to_check:
                if row[field] == '':
                    raise ValueError(f"Empty value found in mandatory column '{field}' for TCID '{row['TCID']}' in API sheet")

    def _validate_body_templates_sheet(self, df: pd.DataFrame):
        required_columns = ['TemplateName', 'Content', 'Format']
        missing_columns = set(required_columns) - set(df.columns)
        if missing_columns:
            raise ValueError(f"Missing required columns in BodyTemplates sheet: {', '.join(missing_columns)}")

        if df['TemplateName'].duplicated().any():
            raise ValueError("Duplicate TemplateName found in BodyTemplates sheet")

        if not df['Format'].isin(['json', 'xml']).all():
            raise ValueError("Invalid values in 'Format' column. Only 'json' or 'xml' are allowed.")

        # Check for empty values in mandatory fields
        for field in required_columns:
            if df[field].eq('').any():
                raise ValueError(f"Empty value found in mandatory column '{field}' in BodyTemplates sheet")

    def _validate_body_defaults_sheet(self, df: pd.DataFrame):
        required_columns = ['Name', 'Content']
        missing_columns = set(required_columns) - set(df.columns)
        if missing_columns:
            raise ValueError(f"Missing required columns in BodyDefaults sheet: {', '.join(missing_columns)}")

        if df['Name'].duplicated().any():
            raise ValueError("Duplicate Name found in BodyDefaults sheet")

        # Check for empty values in mandatory fields
        for field in required_columns:
            if df[field].eq('').any():
                raise ValueError(f"Empty value found in mandatory column '{field}' in BodyDefaults sheet")

        # Validate that Content is valid JSON
        for _, row in df.iterrows():
            try:
                json.loads(row['Content'])
            except json.JSONDecodeError:
                raise ValueError(f"Invalid JSON in BodyDefaults sheet for Name: {row['Name']}")

    def _validate_headers_sheet(self, df: pd.DataFrame):
        required_columns = ['HeaderName', 'Content']
        missing_columns = set(required_columns) - set(df.columns)
        if missing_columns:
            raise ValueError(f"Missing required columns in Headers sheet: {', '.join(missing_columns)}")

        if df['HeaderName'].duplicated().any():
            raise ValueError("Duplicate HeaderName found in Headers sheet")

        # Check for empty values in mandatory fields
        for field in required_columns:
            if df[field].eq('').any():
                raise ValueError(f"Empty value found in mandatory column '{field}' in Headers sheet")

        # Validate that Content is valid YAML
        for _, row in df.iterrows():
            try:
                yaml.safe_load(row['Content'])
            except yaml.YAMLError:
                raise ValueError(f"Invalid YAML in Headers sheet for HeaderName: {row['HeaderName']}")

    def _validate_endpoints_sheet(self, df: pd.DataFrame):
        required_columns = ['Environment', 'Endpoint', 'Method', 'Path']
        missing_columns = set(required_columns) - set(df.columns)
        if missing_columns:
            raise ValueError(f"Missing required columns in Endpoints sheet: {', '.join(missing_columns)}")

        if df.duplicated(subset=['Environment', 'Endpoint']).any():
            raise ValueError("Duplicate Environment-Endpoint combination found in Endpoints sheet")

        valid_methods = ['GET', 'POST', 'PUT', 'DELETE', 'PATCH']
        if not df['Method'].isin(valid_methods).all():
            raise ValueError(f"Invalid values in 'Method' column. Allowed values are: {', '.join(valid_methods)}")

        # Check for empty values in mandatory fields
        for field in required_columns:
            if df[field].eq('').any():
                raise ValueError(f"Empty value found in mandatory column '{field}' in Endpoints sheet")
