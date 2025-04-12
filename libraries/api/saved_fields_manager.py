import logging
import re
import yaml
import os
from typing import Dict, Any
from libraries.common.utility_helpers import PROJECT_ROOT
from robot.libraries.BuiltIn import BuiltIn
from libraries.common.variable_transformer import VariableTransformer

builtin_lib = BuiltIn()


class SavedFieldsManager:
    def __init__(self, file_path: str = None) -> None:
        self.project_root: str = PROJECT_ROOT
        self.file_path: str = file_path or os.path.join(self.project_root, 'configs', 'saved_fields.yaml')
        self.variable_transformer = VariableTransformer()

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

    def load_saved_fields_and_set_robot_global_variables(self) -> None:
        saved_fields: Dict[str, Any] = self.load_saved_fields()
        for key, value in saved_fields.items():
            builtin_lib.set_global_variable(f'${{{key}}}', value)

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
                for column in ['Body Override', 'Exp Result']:
                    if column in test_case and test_case[column] != '':
                        lines = test_case[column].splitlines()
                        replaced_lines = [line.replace(f"${{{key}}}", str(value)) for line in lines]
                        test_case[column] = "\n".join(replaced_lines)
        except Exception as e:
            logging.error(f"{self.__class__.__name__}: Failed to apply saved fields to [Body Override], [Exp Result]: {str(e)}")
            raise

    def apply_suite_variables(self, test_case) -> None:
        try:
            # Enhanced regular expression to match patterns like:
            # assign_value($.result.amount) or
            # assign_value($.result.amount,arg1,arg2,...)
            transform_pattern = re.compile(r'(\w+)\(([^,)]+)(?:,\s*([^)]+))?\)')

            for key in ['Body Override', 'Exp Result']:
                if key not in test_case or not test_case[key]:
                    continue  # Skip empty fields

                lines = test_case[key].splitlines()
                updated_lines = []

                for line in lines:
                    if not line.strip():
                        updated_lines.append(line)  # Preserve empty lines
                        continue

                    # Check if line matches transformation pattern
                    match = transform_pattern.search(line.strip())
                    if match:
                        # Handle transformation format
                        method_name, input_field = match.groups()[0:2]
                        remaining_args_str = match.groups()[2]

                        # Process additional arguments if they exist
                        args = []
                        if remaining_args_str:
                            # Split remaining args by comma and strip whitespace
                            args = [arg.strip() for arg in remaining_args_str.split(',')]

                        # Extract input field value
                        input_value = BuiltIn().get_variable_value(input_field)

                        if input_value is None:
                            logging.warning(f"{self.__class__.__name__}: Robot variable '{input_field}' not found.")

                        # Transform with dynamic arguments
                        transformed_value = self.variable_transformer.transform(method_name, input_value, *args)

                        # Replace entire pattern with transformed value
                        line = transform_pattern.sub(str(transformed_value), line)

                        # Log the transformation
                        args_log = ", ".join([input_field] + args)
                        logging.info(f"{self.__class__.__name__}: [{key}] Applied {method_name}({args_log}) -> [{transformed_value}]")
                    else:
                        # Handle standard variable replacement
                        matches = re.findall(r'\$\{[^}]+\}', line)
                        for match in matches:
                            replacement_value = BuiltIn().get_variable_value(match)
                            line = line.replace(match, str(replacement_value))
                            logging.info(f"{self.__class__.__name__}: [{key}] Replaced {match} with [{replacement_value}]")

                    updated_lines.append(line)

                # Update field content
                test_case[key] = "\n".join(updated_lines)

        except Exception as e:
            logging.error(f"{self.__class__.__name__}: Failed to apply suite variables: {str(e)}")
            raise
