import logging
import os
from typing import Dict, Tuple, List
from robot.api.deco import keyword, library
from libraries.web.web_element_actions import WebElementActions
from libraries.common.utility_helpers import PROJECT_ROOT
from libraries.common.config_manager import ConfigManager
from libraries.web.web_test_loader import WebTestLoader
from libraries.web.webdriver_factory import WebDriverFactory


class WebDriverSingleton:
    _instance = None

    @classmethod
    def get_instance(cls, config_path=None):
        if cls._instance is None:
            if config_path is None:
                raise ValueError("Config path must be provided when creating the first instance")
            cls._instance = WebDriverFactory.create_driver(config_path)
        return cls._instance

    @classmethod
    def quit(cls):
        if cls._instance:
            cls._instance.quit()
            cls._instance = None


@library
class PageObject:
    CONFIG_FILE = 'web_config.yaml'
    CONFIG_DIR = os.path.join(PROJECT_ROOT, 'configs', 'web')

    def __init__(self):
        self.config = self.load_config()
        self.web_test_loader = WebTestLoader(self.config['test_case_path'])
        self.driver = self._load_webdriver()
        self.web_actions = WebElementActions(self.driver)
        self.locators_df = self.web_test_loader.get_locators()
        self.page_object_df = self.web_test_loader.get_page_objects()
        self.page_elements = self._load_page_elements()
        self.page_modules = self._load_page_modules()

    @classmethod
    def load_config(cls) -> Dict:
        config_path = os.path.join(cls.CONFIG_DIR, cls.CONFIG_FILE)
        return ConfigManager.load_yaml(config_path)

    def _load_webdriver(self):
        config_path = os.path.join(self.CONFIG_DIR, self.CONFIG_FILE)
        return WebDriverSingleton.get_instance(config_path)

    def _load_page_elements(self) -> Dict[str, Dict[str, Tuple[str, str]]]:
        elements = {}
        for _, row in self.locators_df.iterrows():
            page_name = row['Page Name']
            element_name = row['Element Name']
            locator = (row['Locator Type'], row['Locator Value'])
            elements.setdefault(page_name, {})[element_name] = locator
        return elements

    def _load_page_modules(self) -> Dict[str, Dict[str, List[Dict]]]:
        modules = {}
        for _, row in self.page_object_df.iterrows():
            page_name = row['Page Name']
            module_name = row['Module Name']
            action_info = {
                'element_name': row['Element Name'],
                'action': row['Actions'],
                'parameter_name': row['Parameter Name'].split(',') if row['Parameter Name'] else []
            }
            modules.setdefault(page_name, {}).setdefault(module_name, []).append(action_info)
        return modules

    @keyword
    def execute_module(self, page_name: str, module_name: str, parameters: Dict = None):
        logging.info(f"Executing module: {module_name} on page: {page_name}")
        parameters = parameters or {}
        module_actions = self.page_modules[page_name][module_name]

        for action_info in module_actions:
            element_name = action_info['element_name']
            action = action_info['action']
            param_names = action_info['parameter_name']

            element = None
            if element_name:
                locator = self.page_elements[page_name][element_name]
                element = self._get_element_with_appropriate_condition(locator, action)

            action_params = [parameters.get(param) for param in param_names]

            msg = f"Executing action: {action}"
            if action_params:
                msg += f" with parameters: {action_params}"
            if element:
                msg += f" on element: {page_name}.{element_name}"
            logging.info(msg)
            self._execute_action(action, element, *action_params)
            logging.info("=" * 80)

    def _get_element_with_appropriate_condition(self, locator: Tuple[str, str], action: str):
        condition_map = {
            'click': 'clickable',
            'select_by_value': 'clickable',
            'select_by_visible_text': 'clickable',
            'select_by_index': 'clickable',
            'double_click': 'clickable',
            'right_click': 'clickable',
            'send_keys': 'visibility',
            'clear': 'visibility',
            'hover': 'visibility',
            'switch_to_frame': 'presence'
        }
        condition = condition_map.get(action, 'presence')
        element = self.web_actions.wait_for_element(locator, condition=condition)
        logging.debug(f"Located element {locator} for action: {action}")
        return element

    def _execute_action(self, action: str, element, *params):
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
        }

        if action not in action_map:
            raise ValueError(f"Unsupported action: {action}")

        return action_map[action](element, *params) if element else action_map[action](*params)
    @keyword
    def close_browser(self):
        WebDriverSingleton.quit()