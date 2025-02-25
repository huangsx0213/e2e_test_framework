import json
import logging
import os
import re
from typing import Dict, Tuple, List
from robot.api.deco import keyword
from libraries.web.web_actions import WebElementActions
from libraries.common.utility_helpers import PROJECT_ROOT
from libraries.common.config_manager import ConfigManager
from libraries.web.web_test_loader import WebTestLoader
from libraries.web.webdriver_factory import WebDriverFactory
from libraries.web.custom_action_executor import CustomActionExecutor
from robot.libraries.BuiltIn import BuiltIn
from libraries.common.db_operator import DBOperator

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


class PageObject:
    def __init__(self, test_config_path: str = None, test_cases_path: str = None):
        self.project_root = PROJECT_ROOT
        self.test_config_path = test_config_path or os.path.join(self.project_root, 'configs', 'web_test_config.yaml')
        self.test_cases_path = test_cases_path or os.path.join(self.project_root, 'test_cases', 'web_test_cases.xlsx')

        self._web_actions_instance = None
        self._driver = None
        self._load_configuration()
        self._initialize_components()
        self.database_operator = DBOperator()

    def _load_configuration(self):
        self.test_config = ConfigManager.load_yaml(self.test_config_path)
        self.web_test_loader = WebTestLoader(self.test_cases_path, self.test_config)
        self.env_config = self._load_environment_config()

    def _load_environment_config(self):
        environments = self.web_test_loader.get_web_environments()
        active_env = self.test_config['active_environment']
        builtin_lib.set_global_variable('${active_environment}', active_env)
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
        self.page_elements = self._load_page_elements()
        self.page_modules = self._load_page_modules()
        self.custom_action_executor = CustomActionExecutor(self.web_test_loader.get_custom_actions())

    @property
    def driver(self):
        if self._driver is None:
            logging.info(f"{self.__class__.__name__}: Driver not yet initialized. It will be initialized when web_actions is used.")
        return self._driver

    @property
    def web_actions(self):
        if self._web_actions_instance is None:
            if self._driver is None:
                active_env_config = self.env_config['environments'][self.test_config['active_environment']]
                self._driver = WebDriverSingleton.get_instance(active_env_config)
                self._driver.minimize_window()
                logging.info(f"{self.__class__.__name__}: Driver initialized lazily for web_actions.")
            self._web_actions_instance = WebElementActions(self._driver)
            logging.info(f"{self.__class__.__name__}: WebElementActions initialized.")
        return self._web_actions_instance

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
                'web_action': row['Actions'],
                'parameter_names': row['Parameter Name'].split(',') if row['Parameter Name'] else [],
                'highlight': row['Highlight'],
                'screen_capture': row['Screenshot'],
                'wait': row['Wait']
            }
            modules.setdefault(row['Page Name'], {}).setdefault(row['Module Name'], []).append(action_info)
        return modules

    @keyword
    def set_environment_variables(self):
        """设置环境变量为Robot Framework全局变量"""
        self.web_test_loader.set_global_variables()

    @keyword
    def execute_module(self, page_name: str, module_name: str, data_set: Dict = None):

        module_actions = self.page_modules[page_name][module_name]

        for action_info in module_actions:
            element_name = action_info['element_name']
            action = action_info['web_action']
            highlight = action_info['highlight']
            screen_capture = action_info['screen_capture']
            wait = action_info['wait']
            locator = self.page_elements[page_name][element_name] if element_name else None
            action_params = self._extract_parameters(data_set, action_info['parameter_names'])
            element_desc = f'{page_name}.{module_name}.{element_name}' if element_name else f'{page_name}.{module_name}'

            logging.info(
                f"{self.__class__.__name__}: Executing action:[{action}] on page:[{page_name}] module:[{module_name}]"
                + (f" element:[{element_name}]" if element_name else "")
                + (f" with parameters:{action_params}" if action_params else "")
            )

            if highlight:
                self.web_actions.highlight_element(locator, element_desc=element_desc)

            self._execute_action(action, locator, element_desc, *action_params)

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

    def _execute_action(self, action: str, locator, element_desc, *args, **kwargs):
        # 定义需要页面元素的操作映射
        element_actions = {
            # ElementActions
            'send_keys': self.web_actions.send_keys,
            'click': self.web_actions.click,
            'clear': self.web_actions.clear,
            'select_by_value': self.web_actions.select_by_value,
            'select_by_visible_text': self.web_actions.select_by_visible_text,
            'select_by_index': self.web_actions.select_by_index,
            'hover': self.web_actions.hover,
            'double_click': self.web_actions.double_click,
            'right_click': self.web_actions.right_click,
            'get_text': self.web_actions.get_text,
            'get_attribute': self.web_actions.get_attribute,
            'select_radio_by_value': self.web_actions.select_radio_by_value,

            # VerificationActions（需要传入element_name用于错误提示或日志记录）
            'verify_text_is': self.web_actions.verify_text_is,
            'verify_figure_is': self.web_actions.verify_figure_is,
            'verify_text_contains': self.web_actions.verify_text_contains,
            'verify_figure_text_contains': self.web_actions.verify_figure_text_contains,
            'verify_title_is': self.web_actions.verify_title_is,
            'verify_title_contains': self.web_actions.verify_title_contains,
            'verify_element_exists': self.web_actions.verify_element_exists,
            'verify_element_visible': self.web_actions.verify_element_visible,
            'verify_element_invisible': self.web_actions.verify_element_invisible,
            'verify_element_clickable': self.web_actions.verify_element_clickable,
            'verify_element_selected': self.web_actions.verify_element_selected,
            'verify_element_enabled': self.web_actions.verify_element_enabled,
            'get_text_save_to_variable': self.web_actions.get_text_save_to_variable,
            'verify_element_value_diff': self.web_actions.verify_element_value_diff,

            # WaitActions（部分等待操作依赖于页面元素）
            'wait_for_element_present': self.web_actions.wait_for_element_present,
            'wait_for_element_visible': self.web_actions.wait_for_element_visible,
            'wait_for_element_invisible': self.web_actions.wait_for_element_invisible,
            'wait_for_element_clickable': self.web_actions.wait_for_element_clickable,
            'wait_for_text_present_in_element': self.web_actions.wait_for_text_present_in_element,
            'wait_for_staleness_of': self.web_actions.wait_for_staleness_of,

            # JavaScriptActions
            'fill_by_js': self.web_actions.fill_by_js,
            'click_by_js': self.web_actions.click_by_js,
            'js_click': self.web_actions.js_click,
            'js_send_keys': self.web_actions.js_send_keys,
            'js_clear': self.web_actions.js_clear,
            'js_scroll_into_view': self.web_actions.js_scroll_into_view,
            'js_scroll_to_element': self.web_actions.js_scroll_to_element,
            'js_select_option': self.web_actions.js_select_option,
            'js_hover': self.web_actions.js_hover,

            # UtilsActions
            'highlight_element': self.web_actions.highlight_element,
        }

        # 定义不依赖页面元素的操作映射
        non_element_actions = {
            # WindowActions
            'switch_to_frame': self.web_actions.switch_to_frame,
            'switch_to_default_content': self.web_actions.switch_to_default_content,
            'switch_to_window': self.web_actions.switch_to_window,
            'get_window_handles': self.web_actions.get_window_handles,
            'close_current_window': self.web_actions.close_current_window,
            'set_window_size': self.web_actions.set_window_size,
            'maximize_window': self.web_actions.maximize_window,
            'minimize_window': self.web_actions.minimize_window,
            'fullscreen_window': self.web_actions.fullscreen_window,

            # JavaScriptActions
            'execute_script': self.web_actions.execute_script,
            'execute_async_script': self.web_actions.execute_async_script,

            # AlertActions
            'accept_alert': self.web_actions.accept_alert,
            'dismiss_alert': self.web_actions.dismiss_alert,
            'get_alert_text': self.web_actions.get_alert_text,

            # CookieActions
            'add_cookie': self.web_actions.add_cookie,
            'get_cookie': self.web_actions.get_cookie,
            'delete_cookie': self.web_actions.delete_cookie,
            'delete_all_cookies': self.web_actions.delete_all_cookies,

            # NavigationActions
            'open_url': self.web_actions.open_url,
            'refresh_page': self.web_actions.refresh_page,
            'go_back': self.web_actions.go_back,
            'go_forward': self.web_actions.go_forward,
            'get_current_url': self.web_actions.get_current_url,

            # TableActions（假定表格相关操作不需要传入element_name）
            'verify_table_exact': self.web_actions.verify_table_exact,
            'verify_table_row_exact': self.web_actions.verify_table_row_exact,
            'verify_specific_cell_exact': self.web_actions.verify_specific_cell_exact,
            'verify_table_partial': self.web_actions.verify_table_partial,
            'verify_table_row_partial': self.web_actions.verify_table_row_partial,
            'verify_specific_cell_partial': self.web_actions.verify_specific_cell_partial,
            'verify_table_regex': self.web_actions.verify_table_regex,
            'verify_table_row_regex': self.web_actions.verify_table_row_regex,
            'verify_specific_cell_regex': self.web_actions.verify_specific_cell_regex,
            'verify_table_is_empty': self.web_actions.verify_table_is_empty,
            'verify_unique_column_values': self.web_actions.verify_unique_column_values,
            'verify_value_in_table': self.web_actions.verify_value_in_table,
            'verify_row_count': self.web_actions.verify_row_count,
            'verify_column_sorted': self.web_actions.verify_column_sorted,
            'select_table_row_checkbox': self.web_actions.select_table_row_checkbox,
            'select_multiple_table_row_checkboxes': self.web_actions.select_multiple_table_row_checkboxes,

            # UtilsActions
            'capture_screenshot': self.web_actions.capture_screenshot,

            # WaitActions（全局等待，不依赖具体的元素）
            'wait': self.web_actions.wait,
        }

        db_actions = {
            "insert_data": self.database_operator.insert_data,
            "update_data": self.database_operator.update_data,
            "delete_data": self.database_operator.delete_data,
        }

        # 先对传入的参数进行变量替换
        new_args = []
        for arg in args:
            if isinstance(arg, str):
                # 使用正则匹配所有 ${...} 格式的变量
                matches = re.findall(r'\$\{([^}]+)\}', arg)
                if matches:
                    for match in matches:
                        replacement_value = builtin_lib.get_variable_value(f'${{{match}}}')
                        arg = arg.replace(f'${{{match}}}', str(replacement_value))
                        logging.info(f"{self.__class__.__name__}: Replaced {match} with value: {replacement_value} for web_action: {action}")
            new_args.append(arg)

        # 判断该动作是否在 element_actions 中，如果在，则加入element_name信息
        if action in element_actions:
            kwargs['element_desc'] = element_desc
            if locator:
                return element_actions[action](locator, *new_args, **kwargs)
            else:
                # 如果 locator 不存在时，可选择报错或者直接调用（取决于具体需求）
                return element_actions[action](*new_args, **kwargs)
        elif action in non_element_actions:
            return non_element_actions[action](*new_args, **kwargs)
        elif action in db_actions:
            return db_actions[action](*new_args, **kwargs)
        elif action in self.custom_action_executor.custom_actions:
            # 如果是自定义操作，继续原有的处理逻辑
            return self.custom_action_executor.execute_custom_action(action, locator, self.web_actions, *new_args, **kwargs)
        else:
            raise ValueError(f"{self.__class__.__name__}: Unsupported web_action: {action}")

    @keyword
    def close_browser(self):
        WebDriverSingleton.quit()

    @keyword
    def sanity_check(self) -> None:
        skip_on_sanity_check_failure = BuiltIn().get_variable_value('${skip_on_sanity_check_failure}', default=False)
        if skip_on_sanity_check_failure:
            BuiltIn().skip("Skipping current test as sanity check failed.")
        else:
            logging.info(f"{self.__class__.__name__}: Sanity check succeeded, continuing with the test.")

    def _extract_parameters(self, data_set: Dict, parameter_names: List[str]) -> List:
        try:
            parameters = []
            if data_set and parameter_names:
                for name in parameter_names:
                    if name in data_set:
                        parameters.append(data_set[name])
                    else:
                        logging.warning(f"{self.__class__.__name__}: Parameter {name} not found in data set")
            return parameters
        except Exception as e:
            logging.error(f"{self.__class__.__name__}: PageObject: Error extracting parameters: {str(e)}")
            raise
