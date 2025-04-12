import json
import logging
import os
import re
from typing import Dict, Tuple, List
from robot.api.deco import keyword
from libraries.api.saved_fields_manager import SavedFieldsManager
from libraries.web.web_actions import WebActions
from libraries.common.utility_helpers import PROJECT_ROOT
from libraries.common.config_manager import ConfigManager
from libraries.web.web_test_loader import WebTestLoader
from libraries.web.webdriver_factory import WebDriverFactory
from libraries.robot.custom_action_executor import CustomActionExecutor
from robot.libraries.BuiltIn import BuiltIn
from libraries.db.db_operator import DBOperator

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


class RobotTestExecutor:
    def __init__(self, test_config_path: str = None, test_cases_path: str = None):
        self.project_root = PROJECT_ROOT
        self.test_config_path = test_config_path or os.path.join(self.project_root, 'configs', 'web_test_config.yaml')
        self.test_cases_path = test_cases_path or os.path.join(self.project_root, 'test_cases', 'web_test_cases.xlsx')

        self._web_actions_instance = None
        self._driver = None
        self._load_configuration()
        self._initialize_components()

    def _load_configuration(self):
        """Load test configurations and initialize loaders"""
        try:
            # Load main test configuration
            self.test_config = ConfigManager.load_yaml(self.test_config_path)
            self.active_env = self.test_config['active_environment']
            if not self.test_config:
                raise ValueError("Empty or invalid test configuration")
            if not self.active_env:
                raise ValueError("Active environment not specified in configuration")

            # Initialize test loaders
            self.web_test_loader = WebTestLoader(self.test_cases_path, self.test_config)
            self.active_db_configs = self.web_test_loader.get_db_configs(self.active_env)

            # Load environment configuration
            self.env_config = self._load_environment_config()

        except Exception as e:
            logging.error(f"Failed to load configuration: {str(e)}")
            raise

    def _load_environment_config(self):
        """Load environment specific configurations"""
        try:
            # Set global variable
            builtin_lib.set_global_variable('${active_environment}', self.active_env)
            # Get environment specific settings
            environments = self.web_test_loader.get_web_environments()
            env_config = environments[environments['Environment'] == self.active_env]
            if env_config.empty:
                raise ValueError(f"Environment '{self.active_env}' not found in configurations")
            # Convert to dict and parse browser options
            env_settings = env_config.iloc[0].to_dict()
            env_settings['BrowserOptions'] = json.loads(env_settings['BrowserOptions'])

            # Return formatted configuration
            return {
                'environments': {
                    self.active_env: {
                        'browser': env_settings['Browser'],
                        'is_remote': env_settings['IsRemote'],
                        'remote_url': env_settings['RemoteURL'],
                        'chrome_path': env_settings['ChromePath'],
                        'chrome_driver_path': env_settings['ChromeDriverPath'],
                        'edge_path': env_settings['EdgePath'],
                        'edge_driver_path': env_settings['EdgeDriverPath'],
                        'browser_options': env_settings['BrowserOptions']
                    }
                }
            }
        except Exception as e:
            logging.error(f"Failed to load environment configuration: {str(e)}")
            raise

    def _initialize_components(self):
        """Initialize test components and load required data"""
        try:
            # Load page related data
            self.locators_df = self.web_test_loader.get_locators()
            self.page_object_df = self.web_test_loader.get_page_objects()
            # Initialize page elements and modules
            self.page_elements = self._load_page_elements()
            self.page_modules = self._load_page_modules()
            # Initialize executors and managers
            self.custom_action_executor = CustomActionExecutor(self.web_test_loader.get_custom_actions())
            self.saved_fields_manager = SavedFieldsManager()
            # Load saved fields and set variables
            self.saved_fields_manager.load_saved_fields_and_set_robot_global_variables()
            self.database_operator = DBOperator(self.active_db_configs)
        except Exception as e:
            logging.error(f"Failed to initialize components: {str(e)}")
            raise

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
                logging.info(f"{self.__class__.__name__}: Driver initialized lazily for web_actions.")
            self._web_actions_instance = WebActions(self._driver)
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
                'wait': row['Wait'],
                'description': row['Descriptions']
            }
            modules.setdefault(row['Page Name'], {}).setdefault(row['Module Name'], []).append(action_info)
        return modules

    @keyword
    def set_environment_variables(self):
        """设置环境变量为Robot Framework全局变量"""
        self.web_test_loader.set_global_variables()

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

    @keyword
    def execute_module(self, page_name: str, module_name: str, data_set: Dict = None):

        module_actions = self.page_modules[page_name][module_name]

        for action_info in module_actions:
            element_name = action_info['element_name']
            action = action_info['web_action']
            highlight = action_info['highlight']
            screen_capture = action_info['screen_capture']
            description = action_info['description']
            wait = action_info['wait']
            locator = self.page_elements[page_name][element_name] if element_name else None
            action_params = self._extract_parameters(data_set, action_info['parameter_names'])
            element_desc = f'{page_name}.{module_name}.{element_name}' if element_name else f'{page_name}.{module_name}'

            logging.info(
                f"{self.__class__.__name__}: Executing action:[{action}] on page:[{page_name}] module:[{module_name}]"
                + (f" element:[{element_name}]" if element_name else "")
                + (f" with parameters:{action_params}" if action_params else "")
            )

            new_args = self._resolve_variable_in_parameters(action_params, action)

            if highlight:
                self.execute_action('highlight_element', locator, element_desc)

            # Unified call to execute_action
            self.execute_action(action, locator, element_desc, *new_args, )

            if wait:
                try:
                    wait_time = float(wait)
                    if wait_time > 0:
                        self.execute_action('wait', locator, element_desc, wait_time)
                except ValueError:
                    logging.warning(f"Invalid wait value: {wait}. Skipping wait.")

            if screen_capture:
                self.execute_action('capture_screenshot', locator, element_desc, description)

            logging.info("=" * 80)

    def execute_action(self, action_name, element, element_desc, *args, **kwargs):
        logging.debug(f"WebActionExecutor: Executing action '{action_name}' with element: {element}, args: {args}, kwargs: {kwargs}")

        db_actions = {
            "insert_data": self.database_operator.insert_data,
            "update_data": self.database_operator.update_data,
            "delete_data": self.database_operator.delete_data,
        }

        if hasattr(self.web_actions, action_name):
            action = getattr(self.web_actions, action_name)

            if 'locator' in action.__code__.co_varnames:
                kwargs['element_desc'] = element_desc
                result = action(element, *args, **kwargs)
            elif 'locator' not in action.__code__.co_varnames:
                result = action(*args, **kwargs)
            else:
                raise ValueError(f"Action '{action_name}' requires a WebElement, but none was provided.")

            logging.debug(f"WebActionExecutor: Action '{action_name}' executed successfully")
            return result
        elif action_name in db_actions:
            db_actions[action_name](*args)
            logging.debug(f"DBActionExecutor: Action '{action_name}' executed successfully")
            return
        elif action_name in self.custom_action_executor.custom_actions:
            self.custom_action_executor.execute_custom_action(action_name, element, self.web_actions, *args)
            logging.debug(f"CustomActionExecutor: Action '{action_name}' executed successfully")
            return
        else:
            error_msg = f"Unsupported action: '{action_name}'"
            logging.error(f"ActionExecutor: {error_msg}")
            raise ValueError(error_msg)

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

    def _resolve_variable_in_parameters(self, action_params, action):
        new_args = []
        # Enhanced regular expression to match patterns like:
        # assign_value($.result.amount) or
        # assign_value($.result.amount,arg1,arg2,...)
        transform_pattern = re.compile(r'(\w+)\(([^,)]+)(?:,\s*([^)]+))?\)')

        for arg in action_params:
            if isinstance(arg, str):
                # First check if the arg matches a transformation pattern
                match = transform_pattern.search(arg.strip())
                if match:
                    method_name, input_field = match.groups()[0:2]
                    remaining_args_str = match.groups()[2]

                    # Process additional arguments if they exist
                    args_list = []
                    if remaining_args_str:
                        # Split remaining args by comma and strip whitespace
                        args_list = [arg.strip() for arg in remaining_args_str.split(',')]

                    # Extract input field value
                    input_value = builtin_lib.get_variable_value(input_field)

                    if input_value is None:
                        logging.warning(f"{self.__class__.__name__}: Robot variable {input_field} not found for web_action: {action} while transforming")

                    # Transform with dynamic arguments
                    transformed_value = self.saved_fields_manager.variable_transformer.transform(method_name, input_value, *args_list)

                    # Replace entire pattern with transformed value
                    arg = transform_pattern.sub(str(transformed_value), arg)

                    # Log the transformation
                    args_log = ", ".join([input_field] + args_list)
                    logging.info(f"{self.__class__.__name__}: Applied {method_name}({args_log}) -> [{transformed_value}] for web_action: {action}")
                else:
                    # Use regular expression to match all ${...} format variables
                    matches = re.findall(r'\$\{([^}]+)\}', arg)
                    if matches:
                        for match in matches:
                            replacement_value = builtin_lib.get_variable_value(f'${{{match}}}')
                            arg = arg.replace(f'${{{match}}}', str(replacement_value))
                            logging.info(
                                f"{self.__class__.__name__}: Replaced {match} with value: {replacement_value} for web_action: {action}"
                            )
            elif isinstance(arg, dict):
                # Handle dictionary arguments
                for key, value in arg.items():
                    if isinstance(value, str):
                        # First check if the value matches a transformation pattern
                        match = transform_pattern.search(value.strip())
                        if match:
                            method_name, input_field = match.groups()[0:2]
                            remaining_args_str = match.groups()[2]

                            # Process additional arguments if they exist
                            args_list = []
                            if remaining_args_str:
                                # Split remaining args by comma and strip whitespace
                                args_list = [a.strip() for a in remaining_args_str.split(',')]

                            # Extract input field value
                            input_value = builtin_lib.get_variable_value(input_field)

                            # Transform with dynamic arguments
                            transformed_value = self.saved_fields_manager.variable_transformer.transform(
                                method_name, input_value, *args_list
                            )

                            # Replace entire pattern with transformed value
                            arg[key] = transform_pattern.sub(str(transformed_value), value)

                            # Log the transformation
                            args_log = ", ".join([input_field] + args_list)
                            logging.info(
                                f"{self.__class__.__name__}: Applied {method_name}({args_log}) -> [{transformed_value}] for web_action: {action}"
                            )
                        else:
                            # Handle regular variable replacements
                            matches = re.findall(r'\$\{([^}]+)\}', value)
                            if matches:
                                for match in matches:
                                    replacement_value = builtin_lib.get_variable_value(f'${{{match}}}')
                                    arg[key] = value.replace(f'${{{match}}}', str(replacement_value))
                                    logging.info(
                                        f"{self.__class__.__name__}: Replaced {match} with value: {replacement_value} for web_action: {action}"
                                    )
            new_args.append(arg)
        return new_args
