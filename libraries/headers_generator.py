import os
import re
import json
from typing import Dict, Any
from .variable_generator import VariableGenerator


class HeadersGenerator:
    def __init__(self, headers_dir: str) -> None:
        self.headers_dir: str = headers_dir

    def prepare_headers(self, headers_filename: str, saved_fields: Dict[str, Any]) -> Dict[str, str]:
        try:
            headers = self._load_headers(headers_filename)
            return {k: self._process_header_value(v, saved_fields) for k, v in headers.items()}
        except KeyError as e:
            raise ValueError(f"Headers file '{headers_filename}' not found: {str(e)}")
        except Exception as e:
            raise ValueError(f"Headers file '{headers_filename}' is not valid: {str(e)}")

    def _load_headers(self, headers_filename: str) -> Dict[str, str]:
        headers_file_path = os.path.join(self.headers_dir, headers_filename)
        if not headers_file_path.endswith('.json'):
            headers_file_path += '.json'
        with open(headers_file_path, 'r') as file:
            headers = json.load(file)
        return headers

    def _process_header_value(self, value: str, saved_fields: Dict[str, Any]) -> str:
        if isinstance(value, str) and re.match(r'\{\{\s*[^}]+?\s*\}\}', value):
            return self._generate_dynamic_value(value, saved_fields)
        return value

    def _generate_dynamic_value(self, template_string: str, saved_fields: Dict[str, Any]) -> str:
        dynamic_key = re.findall(r'\{\{\s*([^}]+?)\s*\}\}', template_string)[0]
        if dynamic_key in saved_fields:
            return saved_fields[dynamic_key]
        return VariableGenerator.generate_dynamic_value(dynamic_key)
