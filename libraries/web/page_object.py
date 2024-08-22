import json
import logging
import os
import re
from typing import Dict, Tuple, List
from robot.api.deco import keyword, library
from libraries.web.web_element_actions import WebElementActions
from libraries.common.utility_helpers import PROJECT_ROOT
from libraries.common.config_manager import ConfigManager
from libraries.web.web_test_loader import WebTestLoader
from libraries.web.webdriver_factory import WebDriverFactory
from robot.libraries.BuiltIn import BuiltIn

builtin_lib = BuiltIn()


class WebDriverSingleton:
    _instance = None

    @classmethod
    def get_instance(cls, driver_config=None):
        logging.info("WebDriverSingleton: Getting WebDriver instance")
        if cls._instance is None:
            if driver_config is None:
                raise ValueError("WebDriverSingleton: Config path must be provided when creating the first instance")
            cls._instance = WebDriverFactory.create_driver(driver_config)
            logging.info("WebDriverSingleton: WebDriver instance created")
        return cls._instance

    @classmethod
    def quit(cls):
        if cls._instance:
            cls._instance.close()
            cls._instance = None
            logging.info("WebDriverSingleton: WebDriver instance closed")


@library
class PageObject:
    def __init__(self, test_config_path: str = None, test_cases_path: str = None):
        self.project_root = PROJECT_ROOT
        self.test_config_path = test_config_path or os.path.join(self.project_root, 'configs', 'web_test_config.yaml')
        self.test_cases_path = test_cases_path or os.path.join(self.project_root, 'test_cases', 'web_test_cases.xlsx')

        self._load_configuration()
        self._initialize_components()

    def _load_configuration(self):
        self.test_config = ConfigManager.load_yaml(self.test_config_path)
        self.web_test_loader = WebTestLoader(self.test_cases_path)
        self.env_config = self._load_environment_config()

    def _load_environment_config(self):
        environments = self.web_test_loader.get_web_environments()
        active_env = self.test_config['active_environment']
        env_config = environments[environments['Environment'] == active_env].iloc[0].to_dict()
        env_config['BrowserOptions'] = json.loads(env_config['BrowserOptions'])

        return {
            'environments': {
                active_env: {
                    'browser': env_config['Browser'],
                    'is_remote': env_config['IsRemote'],
                    'remote_url': env_config['RemoteURL'],
                    'chrome_path': env_config['ChromePath'],
                    'chrome_driver_path': env_config['ChromeDriverPath'],
                    'edge_path': env_config['EdgePath'],
                    'edge_driver_path': env_config['EdgeDriverPath'],
                    'browser_options': env_config['BrowserOptions']
                }
            }
        }

    def _initialize_components(self):
        self.locators_df = self.web_test_loader.get_locators()
        self.page_object_df = self.web_test_loader.get_page_objects()
        self.driver = self._load_webdriver()
        self.web_actions = WebElementActions(self.driver)
        self.page_elements = self._load_page_elements()
        self.page_modules = self._load_page_modules()

    def _load_webdriver(self):
        active_env_config = self.env_config['environments'][self.test_config['active_environment']]
        driver = WebDriverSingleton.get_instance(active_env_config)
        driver.minimize_window()
        return driver

    def _load_page_elements(self) -> Dict[str, Dict[str, Tuple[str, str]]]:
        elements = {}
        for _, row in self.locators_df.iterrows():
            elements.setdefault(row['Page Name'], {})[row['Element Name']] = (row['Locator Type'], row['Locator Value'])
        return elements

    def _load_page_modules(self) -> Dict[str, Dict[str, List[Dict]]]:
        modules = {}
        for _, row in self.page_object_df.iterrows():
            action_info = {
                'element_name': row['Element Name'],
                'action': row['Actions'],
                'parameter_name': row['Parameter Name'].split(',') if row['Parameter Name'] else [],
                'screen_capture': row['Screenshot'],
                'wait': row['Wait']
            }
            modules.setdefault(row['Page Name'], {}).setdefault(row['Module Name'], []).append(action_info)
        return modules

    @keyword
    def execute_module(self, page_name: str, module_name: str, parameters: Dict = None):
        logging.info(f"{self.__class__.__name__}: Executing module: {module_name} on page: {page_name}")
        parameters = parameters or {}
        module_actions = self.page_modules[page_name][module_name]

        for action_info in module_actions:
            element_name = action_info['element_name']
            action = action_info['action']
            screen_capture = action_info['screen_capture']
            wait = action_info['wait']
            element = self._find_element(page_name, element_name, action)
            action_params = [parameters.get(param) for param in action_info['parameter_name']]

            self._execute_action(action, element, *action_params)

            if wait:
                try:
                    wait_time = float(wait)
                    if wait_time > 0:
                        self.web_actions.wait(wait_time)
                except ValueError:
                    logging.warning(f"Invalid wait value: {wait}. Skipping wait.")

            if screen_capture:
                self.web_actions.capture_screenshot()

            logging.info("=" * 80)

    def _find_element(self, page_name: str, element_name: str, action: str):
        if not element_name:
            return None

        locator = self.page_elements[page_name][element_name]
        condition = {
            'click': 'clickable',
            'select_by_value': 'clickable',
            'select_by_visible_text': 'clickable',
            'select_by_index': 'clickable',
            'double_click': 'clickable',
            'right_click': 'clickable',
            'send_keys': 'visibility',
            'clear': 'visibility',
            'hover': 'visibility',
            'highlight_element': 'visibility',
            'switch_to_frame': 'presence'
        }.get(action, 'presence')

        element = self.web_actions.wait_for_element(locator, condition=condition)
        logging.debug(f"{self.__class__.__name__}: Located element {locator} for action: {action}")
        return element

    def _execute_action(self, action: str, element, *args, **kwargs):
        action_map = {
            'open_url': self.web_actions.open_url,
            'send_keys': self.web_actions.send_keys,
            'click': self.web_actions.click,
            'clear': self.web_actions.clear,
            'select_by_value': self.web_actions.select_by_value,
            'select_by_visible_text': self.web_actions.select_by_visible_text,
            'select_by_index': self.web_actions.select_by_index,
            'hover': self.web_actions.hover,
            'double_click': self.web_actions.double_click,
            'right_click': self.web_actions.right_click,
            'scroll_into_view': self.web_actions.scroll_into_view,
            'scroll_to_element': self.web_actions.scroll_to_element,
            'get_text': self.web_actions.get_text,
            'get_attribute': self.web_actions.get_attribute,
            'is_element_present': self.web_actions.is_element_present,
            'is_element_visible': self.web_actions.is_element_visible,
            'is_element_clickable': self.web_actions.is_element_clickable,
            'is_element_selected': self.web_actions.is_element_selected,
            'is_element_enabled': self.web_actions.is_element_enabled,
            'element_text_should_be': self.web_actions.element_text_should_be,
            'element_text_should_contains': self.web_actions.element_text_should_contains,
            'title_should_be': self.web_actions.title_should_be,
            'title_should_contains': self.web_actions.title_should_contains,
            'wait_for_text_to_be_present': self.web_actions.wait_for_text_to_be_present,
            'wait_for_element_to_disappear': self.web_actions.wait_for_element_to_disappear,
            'switch_to_frame': self.web_actions.switch_to_frame,
            'switch_to_default_content': self.web_actions.switch_to_default_content,
            'execute_script': self.web_actions.execute_script,
            'accept_alert': self.web_actions.accept_alert,
            'dismiss_alert': self.web_actions.dismiss_alert,
            'get_alert_text': self.web_actions.get_alert_text,
            'highlight_element': self.web_actions.highlight_element,
            'verify_table_exact': self.web_actions.verify_table_exact,
            'verify_table_row_exact': self.web_actions.verify_table_row_exact,
            'verify_specific_cell_exact': self.web_actions.verify_specific_cell_exact,
            'verify_table_partial': self.web_actions.verify_table_partial,
            'verify_table_row_partial': self.web_actions.verify_table_row_partial,
            'verify_specific_cell_partial': self.web_actions.verify_specific_cell_partial,
            'verify_table_regex': self.web_actions.verify_table_regex,
            'verify_table_row_regex': self.web_actions.verify_table_row_regex,
            'verify_specific_cell_regex': self.web_actions.verify_specific_cell_regex,
            'wait': self.web_actions.wait,
        }

        if action not in action_map:
            raise ValueError(f"{self.__class__.__name__}: Unsupported action: {action}")

        # Create a new list to store the modified arguments
        new_args = []
        for arg in args:
            if isinstance(arg, str):
                # Use regex to find all occurrences of ${...} in the string
                matches = re.findall(r'\$\{([^}]+)\}', arg)
                if matches:
                    for match in matches:
                        # Retrieve the actual value for the variable using builtin_lib
                        replacement_value = builtin_lib.get_variable_value(f'${{{match}}}')
                        # Replace the ${...} placeholder with the actual value
                        arg = arg.replace(f'${{{match}}}', str(replacement_value))

                        logging.info(f"{self.__class__.__name__}: Replaced {match} with value: {replacement_value} for action: {action}")

            # Add the processed (or original) argument to the new list
            new_args.append(arg)

        return action_map[action](element, *new_args, **kwargs) if element else action_map[action](*new_args, **kwargs)

    @keyword
    def close_browser(self):
        WebDriverSingleton.quit()
