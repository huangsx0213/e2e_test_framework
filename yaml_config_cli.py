import argparse
from ruamel.yaml import YAML
import os
from typing import Any, Dict
from libraries.common.utility_helpers import PROJECT_ROOT


class YamlConfigManager:
    """A class for managing YAML configuration files.
    python yaml_config_cli.py configs/api_test_config.yaml --update active_environment PROD --update test_cases_path "test_cases/new_test_cases.xlsx" --update clear_saved_fields_after_test False
    python yaml_config_cli.py configs/api_test_config.yaml --add-to-list tc_id_list TC001 --add-to-list tags api
    python yaml_config_cli.py configs/api_test_config.yaml --remove-from-list tags deprecated
    python yaml_config_cli.py configs/api_test_config.yaml --update active_environment PROD --add-to-list tc_id_list TC001 --remove-from-list tags deprecated
    """
    def __init__(self, file_path: str):
        self.file_path = os.path.join(PROJECT_ROOT, file_path)
        self.yaml = YAML()
        self.yaml.preserve_quotes = True
        self.yaml.indent(mapping=2, sequence=4, offset=2)
        self.config = self.load_yaml()

    def load_yaml(self) -> Dict[str, Any]:
        """Load YAML configuration from the file."""
        if os.path.exists(self.file_path):
            with open(self.file_path, 'r') as file:
                return self.yaml.load(file) or {}
        return {}

    def save_yaml(self):
        """Save YAML configuration to the file."""
        with open(self.file_path, 'w') as file:
            self.yaml.dump(self.config, file)

    def update_config(self, key: str, value: Any):
        """Update the configuration for a given key with the provided value."""
        keys = key.split('.')
        current = self.config
        for k in keys[:-1]:
            if k not in current:
                current[k] = {}
            current = current[k]
        current[keys[-1]] = value
        self.save_yaml()

    def get_config(self, key: str) -> Any:
        """Retrieve the configuration value for a given key."""
        keys = key.split('.')
        current = self.config
        for k in keys:
            if k not in current:
                return None
            current = current[k]
        return current

    def add_to_list(self, key: str, value: Any):
        """Add a value to the list at the given key."""
        current_list = self.get_config(key)
        if current_list is None:
            self.update_config(key, [value])
        elif isinstance(current_list, list):
            if value not in current_list:
                current_list.append(value)
                self.save_yaml()
        else:
            raise ValueError(f"The key '{key}' does not point to a list.")

    def remove_from_list(self, key: str, value: Any):
        """Remove a value from the list at the given key."""
        current_list = self.get_config(key)
        if isinstance(current_list, list):
            if value in current_list:
                current_list.remove(value)
                self.save_yaml()
        else:
            raise ValueError(f"The key '{key}' does not point to a list.")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Manage YAML configuration file.')
    parser.add_argument('file_path', help='Path to the YAML configuration file')
    parser.add_argument('--update', nargs=2, action='append', metavar=('KEY', 'VALUE'),
                        help='Update a configuration value. Can be used multiple times.')
    parser.add_argument('--add-to-list', nargs=2, action='append', metavar=('KEY', 'VALUE'),
                        help='Add a value to a list. Can be used multiple times.')
    parser.add_argument('--remove-from-list', nargs=2, action='append', metavar=('KEY', 'VALUE'),
                        help='Remove a value from a list. Can be used multiple times.')

    args = parser.parse_args()

    yaml_manager = YamlConfigManager(args.file_path)

    if args.update:
        for key, value in args.update:
            # Try to convert the value to the appropriate type
            try:
                value = eval(value)
            except:
                pass  # If conversion fails, keep it as a string
            yaml_manager.update_config(key, value)
            print(f"Updated {key} to {value}")

    if args.add_to_list:
        for key, value in args.add_to_list:
            yaml_manager.add_to_list(key, value)
            print(f"Added {value} to list {key}")

    if args.remove_from_list:
        for key, value in args.remove_from_list:
            yaml_manager.remove_from_list(key, value)
            print(f"Removed {value} from list {key}")

    # Print the updated configuration
    print("\nUpdated configuration:")
    with open(args.file_path, 'r') as file:
        print(file.read())
