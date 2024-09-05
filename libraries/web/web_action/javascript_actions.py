from .base import Base
from .decorators import wait_and_perform
import logging

class JavaScriptActions(Base):
    def execute_script(self, script, *args):
        logging.info(f"{self.__class__.__name__}: Executing JavaScript: {script}, Arguments: {args}")
        result = self.driver.execute_script(script, *args)
        logging.info(f"{self.__class__.__name__}: JavaScript executed successfully, Result: {result}")
        return result

    def execute_async_script(self, script, *args):
        logging.info(f"{self.__class__.__name__}: Executing asynchronous JavaScript: {script}, Arguments: {args}")
        result = self.driver.execute_async_script(script, *args)
        logging.info(f"{self.__class__.__name__}: Asynchronous JavaScript executed successfully, Result: {result}")
        return result

    @wait_and_perform(default_condition="clickable")
    def js_click(self, element):
        element_desc = self._get_element_description(element)
        logging.info(f"{self.__class__.__name__}: Clicking element using JavaScript: {element_desc}")
        self.driver.execute_script("arguments[0].click();", element)
        logging.info(f"{self.__class__.__name__}: Element clicked successfully using JavaScript: {element_desc}")

    @wait_and_perform(default_condition="presence")
    def js_send_keys(self, element, value):
        element_desc = self._get_element_description(element)
        logging.info(f"{self.__class__.__name__}: Sending keys to element using JavaScript: {element_desc}")
        self.driver.execute_script(f"arguments[0].value = '{value}';", element)
        logging.info(f"{self.__class__.__name__}: Keys sent successfully using JavaScript: {element_desc}")

    @wait_and_perform(default_condition="presence")
    def js_clear(self, element):
        element_desc = self._get_element_description(element)
        logging.info(f"{self.__class__.__name__}: Clearing element using JavaScript: {element_desc}")
        self.driver.execute_script("arguments[0].value = '';", element)
        logging.info(f"{self.__class__.__name__}: Element cleared successfully using JavaScript: {element_desc}")

    @wait_and_perform(default_condition="presence")
    def js_scroll_into_view(self, element):
        element_desc = self._get_element_description(element)
        logging.info(f"{self.__class__.__name__}: Scrolling element into view using JavaScript: {element_desc}")
        self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
        logging.info(f"{self.__class__.__name__}: Element scrolled into view successfully using JavaScript: {element_desc}")

    @wait_and_perform(default_condition="presence")
    def js_select_option(self, select_element, option_text):
        element_desc = self._get_element_description(select_element)
        logging.info(f"{self.__class__.__name__}: Selecting option '{option_text}' using JavaScript: {element_desc}")
        self.driver.execute_script(
            "var select = arguments[0];"
            "for(var i = 0; i < select.options.length; i++) {"
            "  if(select.options[i].text == arguments[1]) {"
            "    select.options[i].selected = true;"
            "    var event = new Event('change', { bubbles: true });"
            "    select.dispatchEvent(event);"
            "    break;"
            "  }"
            "}", select_element, option_text
        )
        logging.info(f"{self.__class__.__name__}: Option selected successfully using JavaScript: {element_desc}")

    @wait_and_perform(default_condition="visibility")
    def js_hover(self, element):
        element_desc = self._get_element_description(element)
        logging.info(f"{self.__class__.__name__}: Hovering over element using JavaScript: {element_desc}")
        self.driver.execute_script(
            "var event = new MouseEvent('mouseover', {"
            "  'view': window,"
            "  'bubbles': true,"
            "  'cancelable': true"
            "});"
            "arguments[0].dispatchEvent(event);", element
        )
        logging.info(f"{self.__class__.__name__}: Hovered over element successfully using JavaScript: {element_desc}")
