import yaml
import os
from typing import Dict, Any
from libraries.common.log_manager import logger
from libraries.common.utility_helpers import PROJECT_ROOT


class SavedFieldsManager:
    def __init__(self, file_path: str = None) -> None:
        self.project_root: str = PROJECT_ROOT
        self.file_path: str = file_path or os.path.join(self.project_root, 'configs', 'saved_fields.yaml')

    def load_saved_fields(self) -> Dict[str, Any]:
        if not os.path.exists(self.file_path):
            return {}
        try:
            with open(self.file_path, 'r') as f:
                saved_fields: Dict[str, Any] = yaml.safe_load(f) or {}
            return saved_fields
        except Exception as e:
            logger.error(f"Failed to load saved fields from the yaml file: {str(e)}")
            raise

    def save_fields(self, field_data: Dict[str, Any]) -> None:
        saved_fields: Dict[str, Any] = self.load_saved_fields()
        saved_fields.update(field_data)
        try:
            with open(self.file_path, 'w') as f:
                yaml.safe_dump(saved_fields, f, default_flow_style=False)
        except Exception as e:
            logger.error(f"Failed to save fields to the yaml file: {str(e)}")
            raise

    def apply_saved_fields(self, test_step, saved_fields: Dict, columns: list) -> None:
        try:
            for key, value in saved_fields.items():
                for column in columns:
                    if column in test_step and test_step[column] != '':
                        lines = test_step[column].splitlines()
                        replaced_lines = [line.replace(f"${{{key}}}", str(value)) for line in lines]
                        test_step[column] = "\n".join(replaced_lines)
        except Exception as e:
            logger.error(f"Failed to apply saved fields to [Body Modifications], [Exp Result]: {str(e)}")
            raise
