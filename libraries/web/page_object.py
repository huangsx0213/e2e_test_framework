from libraries.web.web_element_actions import WebElementActions
from libraries.common.log_manager import logger


class PageObject:
    def __init__(self, driver, locators_df, page_object_df):
        self.driver = driver
        self.locators_df = locators_df
        self.page_object_df = page_object_df
        self.web_actions = WebElementActions(driver)
        self.page_elements = self._load_page_elements()
        self.page_methods = self._load_page_methods()

    def _load_page_elements(self):
        elements = {}
        for _, row in self.locators_df.iterrows():
            page_name = row['Page Name']
            element_name = row['Element Name']
            locator_type = row['Locator Type']
            locator_value = row['Locator Value']

            if page_name not in elements:
                elements[page_name] = {}
            elements[page_name][element_name] = (locator_type, locator_value)
        return elements

    def _load_page_methods(self):
        methods = {}
        for _, row in self.page_object_df.iterrows():
            page_name = row['Page Name']
            method_name = row['Method Name']
            element_name = row['Element Name']
            action = row['Actions']
            parameter_name = row['Parameter Name']

            if page_name not in methods:
                methods[page_name] = {}
            methods[page_name][method_name] = {
                'element_name': element_name,
                'action': action,
                'parameter_name': parameter_name.split(',') if parameter_name else []
            }
        return methods

    def execute_method(self, page_name, method_name, parameters=None):
        if parameters is None:
            parameters = {}
        method_info = self.page_methods[page_name][method_name]
        element_name = method_info['element_name']
        action = method_info['action']

        if ',' in action:  # Composite action
            for sub_action in action.split(','):
                self.execute_method(page_name, sub_action, parameters)
        else:
            if element_name:
                locator = self.page_elements[page_name][element_name]
                element = self._get_element_with_appropriate_condition(locator, action)
            else:
                element = None

            if action == 'send_keys':
                self.web_actions.send_keys(element, parameters[method_info['parameter_name'][0]])
            elif action == 'click':
                self.web_actions.click(element)
            elif action == 'clear':
                self.web_actions.clear(element)
            elif action == 'select_by_value':
                self.web_actions.select_by_value(element, parameters[method_info['parameter_name'][0]])
            elif action == 'select_by_visible_text':
                self.web_actions.select_by_visible_text(element, parameters[method_info['parameter_name'][0]])
            elif action == 'select_by_index':
                self.web_actions.select_by_index(element, parameters[method_info['parameter_name'][0]])
            elif action == 'open_url':
                self.web_actions.open_url(parameters[method_info['parameter_name'][0]])
            elif action == 'switch_to_frame':
                self.web_actions.switch_to_frame(element)
            elif action == 'switch_to_default_content':
                self.web_actions.switch_to_default_content()
            elif action == 'accept_alert':
                self.web_actions.accept_alert()
            elif action == 'dismiss_alert':
                self.web_actions.dismiss_alert()
            elif action == 'get_alert_text':
                return self.web_actions.get_alert_text()
            elif action == 'execute_script':
                self.web_actions.execute_script(parameters[method_info['parameter_name'][0]], element)
            else:
                raise ValueError(f"Unsupported action: {action}")

    def _get_element_with_appropriate_condition(self, locator, action):
        if action in ['click', 'select_by_value', 'select_by_visible_text', 'select_by_index']:
            element = self.web_actions.wait_for_element(locator, condition="clickable")
        elif action in ['send_keys', 'clear']:
            element = self.web_actions.wait_for_element(locator, condition="visibility")
        elif action in ['switch_to_frame']:
            element = self.web_actions.wait_for_element(locator, condition="presence")
        else:
            element = self.web_actions.wait_for_element(locator)
        logger.debug(f"Located element {locator} for action: {action}")
        return element
