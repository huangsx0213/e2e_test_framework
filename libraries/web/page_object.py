from libraries.web.web_element_actions import WebElementActions
from libraries.common.log_manager import logger


class PageObject:
    def __init__(self, driver, locators_df, page_object_df):
        self.driver = driver
        self.locators_df = locators_df
        self.page_object_df = page_object_df
        self.web_actions = WebElementActions(driver)
        self.page_elements = self._load_page_elements()
        self.page_modules = self._load_page_modules()

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

    def _load_page_modules(self):
        modules = {}
        for _, row in self.page_object_df.iterrows():
            page_name = row['Page Name']
            module_name = row['Module Name']
            element_name = row['Element Name']
            action = row['Actions']
            parameter_name = row['Parameter Name']

            if page_name not in modules:
                modules[page_name] = {}
            modules[page_name][module_name] = {
                'element_name': element_name,
                'action': action,
                'parameter_name': parameter_name.split(',') if parameter_name else []
            }
        return modules

    def execute_module(self, page_name, module_name, parameters=None):
        if parameters is None:
            parameters = {}
        module_info = self.page_modules[page_name][module_name]
        element_name = module_info['element_name']
        action = module_info['action']

        if element_name:
            locator = self.page_elements[page_name][element_name]
            element = self._get_element_with_appropriate_condition(locator, action)
        else:
            element = None

        if action == 'open_url':
            self.web_actions.open_url(parameters[module_info['parameter_name'][0]])
        elif action == 'send_keys':
            self.web_actions.send_keys(element, parameters[module_info['parameter_name'][0]])
        elif action == 'click':
            self.web_actions.click(element)
        elif action == 'clear':
            self.web_actions.clear(element)
        elif action == 'select_by_value':
            self.web_actions.select_by_value(element, parameters[module_info['parameter_name'][0]])
        elif action == 'select_by_visible_text':
            self.web_actions.select_by_visible_text(element, parameters[module_info['parameter_name'][0]])
        elif action == 'select_by_index':
            self.web_actions.select_by_index(element, parameters[module_info['parameter_name'][0]])
        elif action == 'hover':
            self.web_actions.hover(element)
        elif action == 'double_click':
            self.web_actions.double_click(element)
        elif action == 'right_click':
            self.web_actions.right_click(element)
        elif action == 'scroll_into_view':
            self.web_actions.scroll_into_view(element)
        elif action == 'scroll_to_element':
            self.web_actions.scroll_to_element(element)
        elif action == 'get_text':
            return self.web_actions.get_text(element)
        elif action == 'get_attribute':
            return self.web_actions.get_attribute(element, parameters[module_info['parameter_name'][0]])
        elif action == 'is_element_present':
            return self.web_actions.is_element_present(locator)
        elif action == 'is_element_visible':
            return self.web_actions.is_element_visible(locator, parameters.get('timeout'))
        elif action == 'is_element_clickable':
            return self.web_actions.is_element_clickable(locator, parameters.get('timeout'))
        elif action == 'is_element_selected':
            return self.web_actions.is_element_selected(element)
        elif action == 'is_element_enabled':
            return self.web_actions.is_element_enabled(element)
        elif action == 'element_text_should_be':
            return self.web_actions.element_text_should_be(element, parameters[module_info['parameter_name'][0]])
        elif action == 'element_text_should_contains':
            return self.web_actions.element_text_should_contains(element, parameters[module_info['parameter_name'][0]])
        elif action == 'title_should_be':
            return self.web_actions.title_should_be(parameters[module_info['parameter_name'][0]])
        elif action == 'title_should_contains':
            return self.web_actions.title_should_contains(parameters[module_info['parameter_name'][0]])
        elif action == 'wait_for_text_to_be_present':
            return self.web_actions.wait_for_text_to_be_present(locator, parameters[module_info['parameter_name'][0]])
        elif action == 'wait_for_element_to_disappear':
            return self.web_actions.wait_for_element_to_disappear(locator)
        elif action == 'switch_to_frame':
            self.web_actions.switch_to_frame(element)
        elif action == 'switch_to_default_content':
            self.web_actions.switch_to_default_content()
        elif action == 'execute_script':
            return self.web_actions.execute_script(parameters[module_info['parameter_name'][0]], element)
        elif action == 'accept_alert':
            self.web_actions.accept_alert()
        elif action == 'dismiss_alert':
            self.web_actions.dismiss_alert()
        elif action == 'get_alert_text':
            return self.web_actions.get_alert_text()
        elif action == 'highlight_element':
            self.web_actions.highlight_element(element)
        else:
            raise ValueError(f"Unsupported action: {action}")

    def _get_element_with_appropriate_condition(self, locator, action):
        if action in ['click', 'select_by_value', 'select_by_visible_text', 'select_by_index', 'double_click', 'right_click']:
            element = self.web_actions.wait_for_element(locator, condition="clickable")
        elif action in ['send_keys', 'clear', 'hover']:
            element = self.web_actions.wait_for_element(locator, condition="visibility")
        elif action in ['switch_to_frame']:
            element = self.web_actions.wait_for_element(locator, condition="presence")
        else:
            element = self.web_actions.wait_for_element(locator)
        logger.debug(f"Located element {locator} for action: {action}")
        return element
