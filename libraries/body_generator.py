import json
import os
import re
from typing import Any, Dict, Union
from .config_manager import ConfigManager
from .utility_helpers import UtilityHelpers
from .variable_generator import VariableGenerator
from .template_renderer import TemplateRenderer


class BodyGenerator:
    def __init__(self, template_dir: str, body_defaults_dir: str) -> None:
        self.template_dir = template_dir
        self.body_defaults_dir = body_defaults_dir

    def generate_request_body(self, test_step, default_values_file: str, method) -> (Union[Dict, str], str):
        try:
            if method == 'GET' or method == "DELETE":
                return {}, 'json'
            template_name = test_step['Template']
            body_modifications = json.loads(test_step.get('Body Modifications', '{}'))
            template_path = self._load_template(template_name)
            format_type = UtilityHelpers.get_file_format(template_path)
            body = self.build_body_from_template(template_path, default_values_file, body_modifications, format_type)
            return body, format_type
        except KeyError as e:
            ValueError(f"Template not found: {str(e)}")
        except json.JSONDecodeError as e:
            ValueError("ERROR", f"Failed to decode JSON for body preparation: {str(e)}")
        except Exception as e:
            ValueError(f"ERROR", f"Failed to prepare request body: {str(e)}")

    def _load_template(self, template_name: str) -> str:
        template_path = os.path.join(self.template_dir, f"{template_name}.json")
        # If the JSON file is not found, try with XML extension
        if not os.path.exists(template_path):
            template_path = os.path.join(self.template_dir, f"{template_name}.xml")
        if not os.path.exists(template_path):
            raise ValueError(f"Template '{template_name}' not found in {self.template_dir}")
        return template_path

    def build_body_from_template(self, template_path: str, default_values_file: str, modifications: Dict[str, Any], format_type: str) -> Union[Dict, str]:
        try:
            default_values = self._load_default_body_values(default_values_file)
            # Merge default values and modifications
            body_data = self._integrate_dynamic_defaults(default_values)
            body_data = self._combine_data(body_data, modifications)
            # Generate dynamic values
            dynamic_values = self._generate_dynamic_values(body_data)
            # Merge dynamic values
            body_data = self._combine_data(body_data, dynamic_values)
            return TemplateRenderer.render_template(self.template_dir, template_path, body_data, format_type)
        except KeyError as e:
            raise ValueError(f"Template not found: {str(e)}")
        except Exception as e:
            raise ValueError(f"Failed to build body from template: {str(e)}")

    def _load_default_body_values(self, default_values_file: str) -> Dict[str, Any]:
        file_path = os.path.join(self.body_defaults_dir, default_values_file)
        if not file_path.endswith('.json'):
            file_path += '.json'
        return ConfigManager.load_json(file_path)

    def _integrate_dynamic_defaults(self, default_values: Dict[str, Any]) -> Dict[str, Any]:
        merged_values: Dict[str, Any] = {}
        try:
            for key, value in default_values.items():
                if isinstance(value, dict):
                    merged_values[key] = self._integrate_dynamic_defaults(value)
                elif isinstance(value, str):
                    merged_values[key] = self._replace_dynamic_placeholders(value)
                else:
                    merged_values[key] = value
        except Exception as e:
            raise ValueError(f"Error integrating dynamic value and defaults value: {str(e)}")
        return merged_values

    def _generate_dynamic_values(self, nested_data: Union[Dict[str, Any], list]) -> Union[Dict[str, Any], list]:
        try:
            if isinstance(nested_data, dict):
                return {key: self._generate_dynamic_values(value) if isinstance(value, (dict, list))
                        else self._replace_dynamic_placeholders(value) for key, value in nested_data.items()}
            elif isinstance(nested_data, list):
                return [self._generate_dynamic_values(item) if isinstance(item, (dict, list))
                        else self._replace_dynamic_placeholders(item) for item in nested_data]
        except Exception as e:
            raise ValueError(f"Error generating dynamic values: {str(e)}")
        return nested_data

    def _replace_dynamic_placeholders(self, value: Any) -> Any:
        try:
            if isinstance(value, str) and re.match(r'\{\{\s*[^}]+?\s*\}\}', value):
                dynamic_key = re.findall(r'\{\{\s*([^}]+?)\s*\}\}', value)[0]
                return VariableGenerator.generate_dynamic_value(dynamic_key)
        except Exception as e:
            raise ValueError(f"Error replacing dynamic placeholders '{value}': {str(e)}")
        return value

    def _combine_data(self, base_data: Dict[str, Any], custom_data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            for key, value in custom_data.items():
                if key in base_data and isinstance(value, dict) and isinstance(base_data[key], dict):
                    base_data[key] = self._combine_data(base_data.get(key, {}), value)
                else:
                    base_data[key] = value
        except Exception as e:
            raise ValueError(f"Error combining data: {str(e)}")
        return base_data