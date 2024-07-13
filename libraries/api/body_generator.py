import json
import os
import re
from typing import Any, Dict, Union
from libraries.common.config_manager import ConfigManager
from libraries.common.utility_helpers import UtilityHelpers
from .variable_generator import VariableGenerator
from .template_renderer import TemplateRenderer
from libraries.common.log_manager import logger

class BodyGenerator:
    def __init__(self, template_dir: str, body_defaults_dir: str) -> None:
        self.template_dir = template_dir
        self.body_defaults_dir = body_defaults_dir
        self.format_json = UtilityHelpers.format_json
        self.format_xml = UtilityHelpers.format_xml

    def generate_request_body(self, test_step, default_values_file: str, method) -> (Union[Dict, str], str):
        try:
            if method in ['GET', 'DELETE']:
                return {}, 'json'

            template_name = test_step['Template']
            body_modifications = self._validate_and_load_json(test_step['Body Modifications'], test_step)
            logger.info(f"[TSID:{test_step['TSID']}] Body modifications for test step {test_step['TSID']}: \n{self.format_json(body_modifications)}")
            template_path = self._resolve_template_path(template_name, test_step)
            format_type = UtilityHelpers.get_file_format(template_path)

            # Prepare all required request data
            request_data = self._prepare_request_data(default_values_file, body_modifications, test_step)
            logger.info(f"[TSID:{test_step['TSID']}] Request data for test step {test_step['TSID']}: \n{self.format_json(request_data)}")

            # Generate request body
            body = TemplateRenderer.render_template(self.template_dir, template_path, request_data, format_type)
            if format_type == 'json':
                logger.info(f"[TSID:{test_step['TSID']}] Request body for test step {test_step['TSID']}: \n{self.format_json(body)}")
            else:
                logger.info(f"[TSID:{test_step['TSID']}] Request body for test step {test_step['TSID']}: \n{self.format_xml(body)}")
            return body, format_type
        except Exception as e:
            logger.error(f"[TSID:{test_step['TSID']}] Error in generate_request_body for test step {test_step['TSID']}: {str(e)}")
            raise

    def _validate_and_load_json(self, json_string: str, test_step: Dict[str, Any]) -> Dict[str, Any]:
        try:
            return json.loads(json_string)
        except json.JSONDecodeError:
            logger.error(f"[TSID:{test_step['TSID']}] Invalid JSON format in test step {test_step['TSID']}: {json_string}")
            raise

    def _resolve_template_path(self, template_name: str, test_step: Dict[str, Any]) -> str:
        template_path = os.path.join(self.template_dir, f"{template_name}.json")
        if not os.path.exists(template_path):
            template_path = os.path.join(self.template_dir, f"{template_name}.xml")
        if not os.path.exists(template_path):
            logger.error(f"[TSID:{test_step['TSID']}] Template '{template_name}' not found for test step {test_step['TSID']} in {self.template_dir}")
            raise
        return template_path

    def _prepare_request_data(self, default_values_file: str, modifications: Dict[str, Any],
                              test_step: Dict[str, Any]) -> Dict[str, Any]:
        default_values = self._load_default_values(default_values_file, test_step)
        combined_data = self._merge_values(default_values, modifications, test_step)
        return self._generate_dynamic_values(combined_data, test_step)

    def _load_default_values(self, default_values_file: str, test_step: Dict[str, Any]) -> Dict[str, Any]:
        file_path = os.path.join(self.body_defaults_dir, default_values_file)
        if not file_path.endswith('.json'):
            file_path += '.json'
        if not os.path.exists(file_path):
            logger.error(f"[TSID:{test_step['TSID']}] Default values file '{default_values_file}' not found for test step {test_step['TSID']} in {self.body_defaults_dir}")
            raise
        return ConfigManager.load_json(file_path)

    def _merge_values(self, base_values: Dict[str, Any], custom_values: Dict[str, Any], test_step: Dict[str, Any]) -> \
            Dict[str, Any]:
        try:
            for key, value in custom_values.items():
                if key in base_values and isinstance(value, dict) and isinstance(base_values[key], dict):
                    base_values[key] = self._merge_values(base_values.get(key, {}), value, test_step)
                else:
                    base_values[key] = value
            return base_values
        except Exception as e:
            logger.error(f"[TSID:{test_step['TSID']}] Error merging default values and custom values in test step {test_step['TSID']} : {str(e)}")
            raise

    def _generate_dynamic_values(self, data: Union[Dict[str, Any], list], test_step: Dict[str, Any]) -> Union[
        Dict[str, Any], list]:
        try:
            if isinstance(data, dict):
                return {key: self._generate_dynamic_values(value, test_step) if isinstance(value, (dict, list))
                else self._replace_placeholders(value, test_step) for key, value in data.items()}
            elif isinstance(data, list):
                return [self._generate_dynamic_values(item, test_step) if isinstance(item, (dict, list))
                        else self._replace_placeholders(item, test_step) for item in data]
            return data
        except Exception as e:
            logger.error(f"[TSID:{test_step['TSID']}] Error generating dynamic values in test step {test_step['TSID']} : {str(e)}")
            raise

    def _replace_placeholders(self, value: Any, test_step: Dict[str, Any]) -> Any:
        try:
            if isinstance(value, str) and re.match(r'\{\{\s*[^}]+?\s*\}\}', value):
                placeholder = re.findall(r'\{\{\s*([^}]+?)\s*\}\}', value)[0]
                return VariableGenerator.generate_dynamic_value(placeholder)
            return value
        except Exception as e:
            logger.log("ERROR",
                       f"[TSID:{test_step['TSID']}] Error replacing placeholders in test step {test_step['TSID']} : {str(e)}")
            raise
