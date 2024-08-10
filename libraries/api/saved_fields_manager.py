import logging
import re

import yaml
import os
from typing import Dict, Any
from libraries.common.utility_helpers import PROJECT_ROOT
from robot.libraries.BuiltIn import BuiltIn


builtin_lib = BuiltIn()


class SavedFieldsManager:
    def __init__(self, file_path: str = None) -> None:
        self.project_root: str = PROJECT_ROOT
        self.file_path: str = file_path or os.path.join(self.project_root, 'configs', 'api', 'saved_fields.yaml')

    def clear_saved_fields(self):
        with open(self.file_path, 'w') as f:
            f.write('')

    def load_saved_fields(self) -> Dict[str, Any]:
        if not os.path.exists(self.file_path):
            return {}
        try:
            with open(self.file_path, 'r') as f:
                saved_fields: Dict[str, Any] = yaml.safe_load(f) or {}
            return saved_fields
        except Exception as e:
            logging.error(f"{self.__class__.__name__}: Failed to load saved fields from the yaml file: {str(e)}")
            raise

    def save_fields(self, field_data: Dict[str, Any]) -> None:
        saved_fields: Dict[str, Any] = self.load_saved_fields()
        saved_fields.update(field_data)
        try:
            with open(self.file_path, 'w') as f:
                yaml.safe_dump(saved_fields, f, default_flow_style=False)
        except Exception as e:
            logging.error(f"{self.__class__.__name__}: Failed to save fields to the yaml file: {str(e)}")
            raise

    def apply_saved_fields(self, test_case, saved_fields: Dict) -> None:
        try:
            for key, value in saved_fields.items():
                for column in ['Body Modifications', 'Exp Result']:
                    if column in test_case and test_case[column] != '':
                        lines = test_case[column].splitlines()
                        replaced_lines = [line.replace(f"${{{key}}}", str(value)) for line in lines]
                        test_case[column] = "\n".join(replaced_lines)
        except Exception as e:
            logging.error(f"{self.__class__.__name__}: Failed to apply saved fields to [Body Modifications], [Exp Result]: {str(e)}")
            raise

    def apply_suite_variables(self, test_case) -> None:
        try:
            for key in ['Body Modifications', 'Exp Result']:
                matches = re.findall(r'\$\{[^}]+\}', test_case[key])
                for match in matches:
                    replacement_value = builtin_lib.get_variable_value(f'${{{match}}}')
                    test_case[key] = test_case[key].replace(match, str(replacement_value))
                    logging.info(f"{self.__class__.__name__}: [{key}] Replaced {match} variable value {replacement_value}")

        except Exception as e:
            logging.error(f"{self.__class__.__name__}: [{key}] Replaced {match} with {replacement_value} failed: {str(e)}")
            raise
