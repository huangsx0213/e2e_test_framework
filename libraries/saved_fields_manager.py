import json
import re
import requests
import yaml
import os
import pandas as pd
from typing import Dict, Any


class SavedFieldsManager:
    def __init__(self, file_path: str = 'configs/saved_fields.yaml') -> None:
        self.file_path: str = file_path

    def load_saved_fields(self) -> Dict[str, Any]:
        if not os.path.exists(self.file_path):
            return {}
        try:
            with open(self.file_path, 'r') as f:
                saved_fields: Dict[str, Any] = yaml.safe_load(f) or {}
            return saved_fields
        except Exception as e:
            raise ValueError(f"Failed to load saved fields from the yaml file: {str(e)}")

    def save_fields(self, field_data: Dict[str, Any]) -> None:
        saved_fields: Dict[str, Any] = self.load_saved_fields()
        saved_fields.update(field_data)
        try:
            with open(self.file_path, 'w') as f:
                yaml.safe_dump(saved_fields, f, default_flow_style=False)
        except Exception as e:
            raise ValueError(f"Failed to save fields to the yaml file: {str(e)}")

    def update_saved_fields(self, response: requests.Response, test_step) -> None:
        fields_to_save_lines = self._parse_fields_to_save(test_step.get('Save Fields', ''))
        try:
            actual_response: Dict[str, Any] = response.json()
        except json.JSONDecodeError as e:
            raise ValueError(
                f"Failed to parse response as JSON while updating the saved files to the yaml file: {str(e)}")
        field_data = {
            f"{test_step['TSID']}.{field}": self._extract_value(actual_response, field)
            for field in fields_to_save_lines
        }
        self.save_fields(field_data)

    def _parse_fields_to_save(self, fields_to_save: str) -> list:
        return fields_to_save.strip().split('\n') if pd.notna(fields_to_save) else []

    def _extract_value(self, actual_response: Dict[str, Any], field_path: str) -> Any:
        parts = field_path.split('.')
        try:
            if isinstance(actual_response, list) and 'response[' in parts[0]:
                match = re.match(r'response\[(\d+)\]', parts[0])
                array_index = int(match.group(1))
                value = actual_response[array_index]
            else:
                value = actual_response

            for part in parts[1:]:
                if '[' in part and ']' in part:
                    array_part, idx = re.match(r'(.*)\[(\d+)\]', part).groups()
                    value = value[array_part][int(idx)]
                else:
                    value = value[part]
            return value
        except (KeyError, IndexError, TypeError) as e:
            raise ValueError(f"KeyError/IndexError/TypeError while handling _extract_value to the yaml file: {str(e)}")

    def apply_saved_fields(self, test_step, saved_fields: Dict, columns: list) -> None:
        try:
            for key, value in saved_fields.items():
                for column in columns:
                    if column in test_step and test_step[column] != '':
                        lines = test_step[column].splitlines()
                        replaced_lines = [line.replace(f"${{{key}}}", str(value)) for line in lines]
                        test_step[column] = "\n".join(replaced_lines)
        except Exception as e:
            logger.log("ERROR", f"Failed to apply saved fields to [Body Modifications], [Exp Result]: {str(e)}")
            raise
