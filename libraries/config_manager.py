import yaml
import json
import os
from typing import Dict


class ConfigManager:

    @staticmethod
    def load_json(file_path: str) -> Dict:
        with open(file_path, 'r') as file:
            config = json.load(file)
        return config

    @staticmethod
    def load_yaml(file_path: str) -> Dict:
        with open(file_path, 'r') as file:
            config = yaml.safe_load(file)
        return config

    @staticmethod
    def load_templates(template_dir: str) -> Dict[str, str]:
        templates = {}
        for filename in os.listdir(template_dir):
            if filename.endswith('.json') or filename.endswith('.xml'):
                template_name = os.path.splitext(filename)[0]
                templates[template_name] = os.path.join(template_dir, filename)
        return templates
