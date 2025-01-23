import json
import logging
import pandas as pd
import yaml
from typing import List, Dict

class APITestLoader:
    _instances = {}

    def __new__(cls, excel_path: str):
        if excel_path not in cls._instances:
            instance = super().__new__(cls)
            instance.__init__(excel_path)
            cls._instances[excel_path] = instance
        return cls._instances[excel_path]

    def __init__(self, excel_path: str):
        if hasattr(self, 'initialized'):
            return
        self.excel_path = excel_path
        self.data: Dict[str, pd.DataFrame] = {}
        self._load_all_excel_data()
        self.validate_excel_structure()
        self.initialized = True

    def _load_all_excel_data(self):
        try:
            excel_file = pd.ExcelFile(self.excel_path)
            for sheet_name in excel_file.sheet_names:
                self.data[sheet_name] = excel_file.parse(sheet_name).fillna('')
            excel_file.close()
        except Exception as e:
            logging.error(f"{self.__class__.__name__}: Error loading Excel file: {e}")
            raise ValueError(f"Error loading Excel file: {e}")

    def validate_excel_structure(self):
        required_sheets = ['API', 'BodyTemplates', 'BodyDefaults', 'Headers', 'Endpoints']
        missing_sheets = set(required_sheets) - set(self.data.keys())
        if missing_sheets:
            logging.error(f"{self.__class__.__name__}: Missing required sheets: {', '.join(missing_sheets)}")
            raise ValueError(f"Missing required sheets: {', '.join(missing_sheets)}")

        for sheet_name, df in self.data.items():
            self.validate_sheet_data(sheet_name, df)

    def get_data(self, sheet_name: str) -> pd.DataFrame:
        if sheet_name not in self.data:
            raise ValueError(f"Sheet '{sheet_name}' not found in the Excel file")
        return self.data[sheet_name]

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

    def filter_cases(self, tcid_list: List[str] = None, tags: List[str] = None) -> pd.DataFrame:
        test_cases = self.get_api_test_cases()

        if tcid_list:
            test_cases = test_cases[test_cases['TCID'].isin(tcid_list)]

        if tags:
            test_cases = test_cases[test_cases['Tags'].apply(lambda x: any(tag in str(x).split(',') for tag in tags))]

        return test_cases[test_cases['Run'] == 'Y']

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
        required_columns = ['TCID', 'Run', 'Endpoint', 'Body Template', 'Body Default', 'Body Override', 'Headers', 'Exp Result']
        self._check_required_columns(df, required_columns, 'API')

        if df['TCID'].duplicated().any():
            raise ValueError("Duplicate TCID found in API sheet")

        if not df['Run'].isin(['Y', 'N']).all():
            raise ValueError("Invalid values in 'Run' column. Only 'Y' or 'N' are allowed.")

        for _, row in df.iterrows():
            self._validate_api_row(row)

    def _validate_api_row(self, row: pd.Series):
        method = self.get_endpoints().loc[self.get_endpoints()['Endpoint'] == row['Endpoint'], 'Method'].iloc[0]

        # Validate references to other sheets
        self._validate_sheet_reference(row['Body Template'], 'BodyTemplates', 'TemplateName', row['TCID'])
        self._validate_sheet_reference(row['Body Default'], 'BodyDefaults', 'Name', row['TCID'])
        self._validate_sheet_reference(row['Headers'], 'Headers', 'HeaderName', row['TCID'])
        self._validate_sheet_reference(row['Endpoint'], 'Endpoints', 'Endpoint', row['TCID'])

        # Validate mandatory fields based on HTTP method
        if method in ['GET', 'DELETE']:
            mandatory_fields = ['TCID', 'Endpoint', 'Headers', 'Exp Status']
        else:
            mandatory_fields = ['TCID', 'Endpoint', 'Body Template', 'Body Default', 'Headers', 'Exp Status']

        for field in mandatory_fields:
            if pd.isna(row[field]) or row[field] == '':
                raise ValueError(f"Empty value found in mandatory column '{field}' for TCID '{row['TCID']}' in API sheet")

    def _validate_body_templates_sheet(self, df: pd.DataFrame):
        required_columns = ['TemplateName', 'Content', 'Format']
        self._check_required_columns(df, required_columns, 'BodyTemplates')

        if df['TemplateName'].duplicated().any():
            raise ValueError("Duplicate TemplateName found in BodyTemplates sheet")

        if not df['Format'].isin(['json', 'xml']).all():
            raise ValueError("Invalid values in 'Format' column. Only 'json' or 'xml' are allowed.")

    def _validate_body_defaults_sheet(self, df: pd.DataFrame):
        required_columns = ['Name', 'Content']
        self._check_required_columns(df, required_columns, 'BodyDefaults')

        if df['Name'].duplicated().any():
            raise ValueError("Duplicate Name found in BodyDefaults sheet")

        for _, row in df.iterrows():
            try:
                yaml.safe_load(row['Content'])
            except yaml.YAMLError as e:
                raise ValueError(f"Invalid YAML in BodyDefaults sheet for Name: {row['Name']}. Error: {e}")

    def _validate_headers_sheet(self, df: pd.DataFrame):
        required_columns = ['HeaderName', 'Content']
        self._check_required_columns(df, required_columns, 'Headers')

        if df['HeaderName'].duplicated().any():
            raise ValueError("Duplicate HeaderName found in Headers sheet")

        for _, row in df.iterrows():
            try:
                yaml.safe_load(row['Content'])
            except yaml.YAMLError:
                raise ValueError(f"Invalid YAML in Headers sheet for HeaderName: {row['HeaderName']}")

    def _validate_endpoints_sheet(self, df: pd.DataFrame):
        required_columns = ['Environment', 'Endpoint', 'Method', 'Path']
        self._check_required_columns(df, required_columns, 'Endpoints')

        if df.duplicated(subset=['Environment', 'Endpoint']).any():
            raise ValueError("Duplicate Environment-Endpoint combination found in Endpoints sheet")

        valid_methods = ['GET', 'POST', 'PUT', 'DELETE', 'PATCH']
        if not df['Method'].isin(valid_methods).all():
            raise ValueError(f"Invalid values in 'Method' column. Allowed values are: {', '.join(valid_methods)}")

    def _check_required_columns(self, df: pd.DataFrame, required_columns: List[str], sheet_name: str):
        missing_columns = set(required_columns) - set(df.columns)
        if missing_columns:
            raise ValueError(f"Missing required columns in {sheet_name} sheet: {', '.join(missing_columns)}")

    def _validate_sheet_reference(self, value: str, sheet_name: str, column_name: str, tcid: str):
        if value:
            referenced_sheet = self.get_data(sheet_name)
            if value not in referenced_sheet[column_name].values:
                raise ValueError(f"Referenced value '{value}' in '{sheet_name}' sheet not found for TCID '{tcid}'")