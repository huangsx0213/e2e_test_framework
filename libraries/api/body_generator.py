import json
import logging
import re

from typing import Any, Dict, Union
from libraries.common.utility_helpers import UtilityHelpers
from libraries.api.template_renderer import TemplateRenderer
from libraries.api.variable_generator import VariableGenerator


class BodyGenerator:
    def __init__(self, api_test_loader):
        self.api_test_loader = api_test_loader
        self.format_json = UtilityHelpers.format_json
        self.format_xml = UtilityHelpers.format_xml

    def generate_request_body(self, test_case, method) -> (Union[Dict, str], str):
        try:
            if method in ['GET', 'DELETE']:
                return {}, 'json'

            template_content, template_format = self.load_template(test_case['Body Template'])
            default_values = self.load_default_values(test_case['Body Default'])
            user_defined_fields = self.parse_user_defined_fields(test_case['Body Override'])
            logging.info(f"{self.__class__.__name__}:Body Override for test case {test_case['TCID']}: \n{user_defined_fields}")
            combined_data = self.merge_values(default_values, user_defined_fields, test_case)
            request_data = self.generate_dynamic_values(combined_data, test_case)
            logging.info(f"{self.__class__.__name__}:Request data for test case {test_case['TCID']}: \n{self.format_json(request_data)}")

            # Generating request body
            body = TemplateRenderer.render_template(template_content, request_data, template_format)
            if template_format == 'json':
                logging.info(f"{self.__class__.__name__}:Request body for test case {test_case['TCID']}: \n{self.format_json(body)}")
            else:
                logging.info(f"{self.__class__.__name__}:Request body for test case {test_case['TCID']}: \n{self.format_xml(body)}")
            return body, template_format
        except Exception as e:
            logging.error(f"{self.__class__.__name__}:Error in generate_request_body for test case {test_case['TCID']}: {str(e)}")
            raise

    def load_template(self, template_name):
        templates = self.api_test_loader.get_body_templates()
        try:
            template = templates[templates['TemplateName'] == template_name]
            if template.empty:
                raise ValueError(f"Template '{template_name}' not found.")
            content = template.iloc[0]['Content']
            format = template.iloc[0]['Format']
            return content, format
        except Exception as e:
            logging.error(f"Error loading template: {e}")
            raise

    def load_default_values(self, default_name):
        defaults = self.api_test_loader.get_body_defaults()
        try:
            default = defaults[defaults['Name'] == default_name]
            if default.empty:
                raise ValueError(f"Default values '{default_name}' not found.")
            return json.loads(default.iloc[0]['Content'])
        except Exception as e:
            logging.error(f"Error loading default values: {e}")
            raise

    def parse_user_defined_fields(self, field_string):
        try:
            return json.loads(field_string)
        except json.JSONDecodeError as e:
            logging.error(f"Error parsing user-defined fields: {e}")
            raise

    def merge_values(self, base_values: Dict[str, Any], custom_values: Dict[str, Any], test_case: Dict[str, Any]) -> Dict[str, Any]:
        try:
            for key, value in custom_values.items():
                if key in base_values and isinstance(value, dict) and isinstance(base_values[key], dict):
                    base_values[key] = self.merge_values(base_values.get(key, {}), value, test_case)
                else:
                    base_values[key] = value
            return base_values
        except Exception as e:
            logging.error(f"{self.__class__.__name__}:Error merging default values and custom values in test case {test_case['TCID']} : {str(e)}")
            raise

    def generate_dynamic_values(self, data: Union[Dict[str, Any], list], test_case: Dict[str, Any]) -> Union[
        Dict[str, Any], list]:
        try:
            if isinstance(data, dict):
                return {key: self.generate_dynamic_values(value, test_case) if isinstance(value, (dict, list))
                        else self.replace_placeholders(value, test_case) for key, value in data.items()}
            elif isinstance(data, list):
                return [self.generate_dynamic_values(item, test_case) if isinstance(item, (dict, list))
                        else self.replace_placeholders(item, test_case) for item in data]
            return data
        except Exception as e:
            logging.error(f"{self.__class__.__name__}:Error generating dynamic values in test case {test_case['TCID']} : {str(e)}")
            raise

    def replace_placeholders(self, value: Any, test_case) -> Any:
        try:
            if isinstance(value, str) and re.match(r'\{\{\s*[^}]+?\s*\}\}', value):
                placeholder = re.findall(r'\{\{\s*([^}]+?)\s*\}\}', value)[0]
                return VariableGenerator.generate_dynamic_value(placeholder)
            return value
        except Exception as e:
            logging.error(f"{self.__class__.__name__}:Error replacing placeholders in test case {test_case['TCID']}: {str(e)}")
            raise
