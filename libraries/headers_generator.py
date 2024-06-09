import os
import re
import json
from typing import Dict, Any
from .variable_generator import VariableGenerator

class HeadersGenerator:
    def __init__(self, headers_dir: str) -> None:
        self.headers_dir: str = headers_dir

    def prepare_headers(self, headers_filename: str, saved_fields: Dict[str, Any], test_step: Dict[str, Any]) -> Dict[str, str]:
        try:
            headers = self._load_headers(headers_filename, test_step)
            return {k: self._replace_placeholders(v, saved_fields, headers_filename, test_step) for k, v in headers.items()}
        except KeyError as e:
            raise ValueError(f"Headers file '{headers_filename}' not found in test step '{test_step['TSID']}': {str(e)}")
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON format in headers file '{headers_filename}' for test step '{test_step['TSID']}': {str(e)}")
        except Exception as e:
            raise ValueError(f"Error processing headers file '{headers_filename}' for test step '{test_step['TSID']}': {str(e)}")

    def _load_headers(self, headers_filename: str, test_step: Dict[str, Any]) -> Dict[str, str]:
        """Load headers from a JSON file."""
        try:
            headers_file_path = os.path.join(self.headers_dir, headers_filename)
            if not headers_file_path.endswith('.json'):
                headers_file_path += '.json'
            if not os.path.exists(headers_file_path):
                raise ValueError(f"Headers file '{headers_filename}' not found in directory '{self.headers_dir}' for test step '{test_step['TSID']}'")
            with open(headers_file_path, 'r') as file:
                headers = json.load(file)
            return headers
        except Exception as e:
            raise ValueError(f"Error loading headers file '{headers_filename}' for test step '{test_step['TSID']}': {str(e)}")

    def _replace_placeholders(self, value: Any, saved_fields: Dict[str, Any], headers_filename: str, test_step: Dict[str, Any]) -> Any:
        """Replace dynamic placeholders in the string."""
        try:
            if isinstance(value, str) and re.match(r'\{\{\s*[^}]+?\s*\}\}', value):
                placeholder = re.findall(r'\{\{\s*([^}]+?)\s*\}\}', value)[0]
                if placeholder in saved_fields:
                    return saved_fields[placeholder]
                return VariableGenerator.generate_dynamic_value(placeholder)
            return value
        except Exception as e:
            raise ValueError(f"Error replacing placeholders in headers file '{headers_filename}' for test step '{test_step['TSID']}': {str(e)}")