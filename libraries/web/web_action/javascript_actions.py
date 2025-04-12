from .base import Base
import logging
from .js import click_by_js_script, fill_by_js_script


class JavaScriptActions(Base):
    def execute_script(self, script, *args):
        logging.debug(f"{self.__class__.__name__}: Executing JavaScript: {script}, Arguments: {args}")
        result = self.driver.execute_script(script, *args)
        logging.info(f"{self.__class__.__name__}: JavaScript executed successfully, Result: {result}")
        return result

    def execute_async_script(self, script, *args):
        logging.debug(f"{self.__class__.__name__}: Executing asynchronous JavaScript: {script}, Arguments: {args}")
        result = self.driver.execute_async_script(script, *args)
        logging.info(f"{self.__class__.__name__}: Asynchronous JavaScript executed successfully, Result: {result}")
        return result

    def js_scroll_into_view(self, locator, element_desc=None, condition="presence"):
        element = self._resolve_element(locator, element_desc, condition)
        element_desc = element_desc or self._get_element_description(locator)
        logging.debug(f"{self.__class__.__name__}: Scrolling element [ {element_desc}:{locator} ] into view using JavaScript.")
        self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
        logging.info(f"{self.__class__.__name__}: Scrolled element [ {element_desc}:{locator} ] into view using JavaScript successfully.")

    def js_scroll_to_element(self, locator, element_desc=None, condition="presence"):
        element = self._resolve_element(locator, element_desc, condition)
        element_desc = element_desc or self._get_element_description(locator)
        logging.debug(f"{self.__class__.__name__}: Scrolling to element [ {element_desc}:{locator} ] with smooth behavior using JavaScript.")
        self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center', inline: 'nearest'});", element)
        logging.info(f"{self.__class__.__name__}: Scrolled to element [ {element_desc}:{locator} ] with smooth behavior using JavaScript successfully.")

    def click_by_js(self, locator, element_desc=None, condition="clickable"):
        element = self._resolve_element(locator, element_desc, condition)
        element_desc = element_desc or self._get_element_description(locator)
        logging.debug(f"{self.__class__.__name__}: Clicking element [ {element_desc}:{locator} ] using JavaScript.")
        js = click_by_js_script
        self.driver.execute_script(js, element)
        logging.info(f"{self.__class__.__name__}: Clicked element [ {element_desc}:{locator} ] using JavaScript successfully.")

    def fill_by_js(self, locator, value, element_desc=None, condition="presence"):
        element = self._resolve_element(locator, element_desc, condition)
        element_desc = element_desc or self._get_element_description(locator)
        logging.debug(f"{self.__class__.__name__}: Sending keys to element [ {element_desc}:{locator} ] using JavaScript with value: [ {value} ].")
        js = fill_by_js_script.format(text=value)
        self.driver.execute_script(js, element)
        logging.info(f"{self.__class__.__name__}: Sent keys to element [ {element_desc}:{locator} ] using JavaScript with value: [ {value} ] successfully.")

    def js_click(self, locator, element_desc=None, condition="clickable"):
        element = self._resolve_element(locator, element_desc, condition)
        element_desc = element_desc or self._get_element_description(locator)
        logging.debug(f"{self.__class__.__name__}: Clicking element [ {element_desc}:{locator} ] using JavaScript.")
        self.driver.execute_script("arguments[0].click();", element)
        logging.info(f"{self.__class__.__name__}: Clicked element [ {element_desc}:{locator} ] using JavaScript successfully.")

    def js_send_keys(self, locator, value, element_desc=None, condition="presence"):
        element = self._resolve_element(locator, element_desc, condition)
        element_desc = element_desc or self._get_element_description(locator)
        logging.debug(f"{self.__class__.__name__}: Sending keys to element [ {element_desc}:{locator} ] using JavaScript with value: [ {value} ].")
        self.driver.execute_script(f"arguments[0].value = '{value}';", element)
        logging.info(f"{self.__class__.__name__}: Sent keys to element [ {element_desc}:{locator} ] using JavaScript with value: [ {value} ] successfully.")

    def js_clear(self, locator, element_desc=None, condition="presence"):
        element = self._resolve_element(locator, element_desc, condition)
        element_desc = element_desc or self._get_element_description(locator)
        logging.debug(f"{self.__class__.__name__}: Clearing element [ {element_desc}:{locator} ] using JavaScript.")
        self.driver.execute_script("arguments[0].value = '';", element)
        logging.info(f"{self.__class__.__name__}: Cleared element [ {element_desc}:{locator} ] using JavaScript successfully.")

    def js_select_option(self, locator, option_text, element_desc=None, condition="presence"):
        element = self._resolve_element(locator, element_desc, condition)
        element_desc = element_desc or self._get_element_description(locator)
        logging.debug(f"{self.__class__.__name__}: Selecting option [ {option_text} ] for element [ {element_desc}:{locator} ] using JavaScript.")
        self.driver.execute_script(
            "var select = arguments[0];"
            "for(var i = 0; i < select.options.length; i++) {"
            "  if(select.options[i].text == arguments[1]) {"
            "    select.options[i].selected = true;"
            "    var event = new Event('change', { bubbles: true });"
            "    select.dispatchEvent(event);"
            "    break;"
            "  }"
            "}", element, option_text
        )
        logging.info(f"{self.__class__.__name__}: Selected option [ {option_text} ] for element [ {element_desc}:{locator} ] using JavaScript successfully.")

    def js_hover(self, locator, element_desc=None, condition="visibility"):
        element = self._resolve_element(locator, element_desc, condition)
        element_desc = element_desc or self._get_element_description(locator)
        logging.debug(f"{self.__class__.__name__}: Hovering over element [ {element_desc}:{locator} ] using JavaScript.")
        self.driver.execute_script(
            "var event = new MouseEvent('mouseover', {"
            "  'view': window,"
            "  'bubbles': true,"
            "  'cancelable': true"
            "});"
            "arguments[0].dispatchEvent(event);", element
        )
        logging.info(f"{self.__class__.__name__}: Hovered over element [ {element_desc}:{locator} ] using JavaScript successfully.")
