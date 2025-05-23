from selenium.webdriver import ActionChains, Keys
from selenium.webdriver.support.select import Select
import logging
from .base import Base


class ElementActions(Base):
    def send_keys(self, locator, value, element_desc=None, condition="presence"):
        element = self._resolve_element(locator, element_desc, condition)
        element_desc = element_desc or self._get_element_description(locator)
        logging.debug(f"{self.__class__.__name__}: Sending keys to element [ {element_desc}:{locator} ] with value: [ {value} ].")
        element.send_keys(value)
        logging.info(f"{self.__class__.__name__}: Sent keys to element [ {element_desc}:{locator} ] with value: [ {value} ] successfully.")

    def click(self, locator, element_desc=None, condition="clickable"):
        element = self._resolve_element(locator, element_desc, condition)
        element_desc = element_desc or self._get_element_description(locator)
        logging.debug(f"{self.__class__.__name__}: Clicking element [ {element_desc}:{locator} ].")
        element.click()
        logging.info(f"{self.__class__.__name__}: Clicked element [ {element_desc}:{locator} ] successfully.")

    def clear(self, locator, element_desc=None, condition="presence"):
        element = self._resolve_element(locator, element_desc, condition)
        element_desc = element_desc or self._get_element_description(locator)
        logging.debug(f"{self.__class__.__name__}: Clearing element [ {element_desc}:{locator} ].")
        element.clear()
        logging.info(f"{self.__class__.__name__}: Cleared element [ {element_desc}:{locator} ] successfully.")

    def get_text(self, locator, element_desc=None, condition="presence"):
        element = self._resolve_element(locator, element_desc, condition)
        element_desc = element_desc or self._get_element_description(locator)
        logging.debug(f"{self.__class__.__name__}: Getting text from element [ {element_desc}:{locator} ].")
        text = element.text
        logging.info(f"{self.__class__.__name__}: Got text '{text}' from element [ {element_desc}:{locator} ] successfully.")
        return text

    def get_attribute(self, locator, attribute_name, element_desc=None, condition="presence"):
        element = self._resolve_element(locator, element_desc, condition)
        element_desc = element_desc or self._get_element_description(locator)
        logging.debug(f"{self.__class__.__name__}: Getting attribute '{attribute_name}' from element [ {element_desc}:{locator} ].")
        attribute_value = element.get_attribute(attribute_name)
        logging.info(f"{self.__class__.__name__}: Got attribute '{attribute_name}'='{attribute_value}' from element [ {element_desc}:{locator} ] successfully.")
        return attribute_value

    def select_by_value(self, locator, value, element_desc=None, condition="presence"):
        element = self._resolve_element(locator, element_desc, condition)
        element_desc = element_desc or self._get_element_description(locator)
        logging.debug(f"{self.__class__.__name__}: Selecting option by value '{value}' for element [ {element_desc}:{locator} ].")
        Select(element).select_by_value(value)
        logging.info(f"{self.__class__.__name__}: Selected option by value '{value}' for element [ {element_desc}:{locator} ] successfully.")

    def select_by_visible_text(self, locator, text, element_desc=None, condition="presence"):
        element = self._resolve_element(locator, element_desc, condition)
        element_desc = element_desc or self._get_element_description(locator)
        logging.debug(f"{self.__class__.__name__}: Selecting option by visible text '{text}' for element [ {element_desc}:{locator} ].")
        Select(element).select_by_visible_text(text)
        logging.info(f"{self.__class__.__name__}: Selected option by visible text '{text}' for element [ {element_desc}:{locator} ] successfully.")

    def select_by_index(self, locator, index, element_desc=None, condition="presence"):
        element = self._resolve_element(locator, element_desc, condition)
        element_desc = element_desc or self._get_element_description(locator)
        logging.debug(f"{self.__class__.__name__}: Selecting option at index '{index}' for element [ {element_desc}:{locator} ].")
        Select(element).select_by_index(int(index))
        logging.info(f"{self.__class__.__name__}: Selected option at index '{index}' for element [ {element_desc}:{locator} ] successfully.")

    def hover(self, locator, element_desc=None, condition="visibility"):
        element = self._resolve_element(locator, element_desc, condition)
        element_desc = element_desc or self._get_element_description(locator)
        logging.debug(f"{self.__class__.__name__}: Hovering over element [ {element_desc}:{locator} ].")
        ActionChains(self.driver).move_to_element(element).perform()
        logging.info(f"{self.__class__.__name__}: Hovered over element [ {element_desc}:{locator} ] successfully.")

    def double_click(self, locator, element_desc=None, condition="clickable"):
        element = self._resolve_element(locator, element_desc, condition)
        element_desc = element_desc or self._get_element_description(locator)
        logging.debug(f"{self.__class__.__name__}: Double clicking element [ {element_desc}:{locator} ].")
        ActionChains(self.driver).double_click(element).perform()
        logging.info(f"{self.__class__.__name__}: Double clicked element [ {element_desc}:{locator} ] successfully.")

    def right_click(self, locator, element_desc=None, condition="clickable"):
        element = self._resolve_element(locator, element_desc, condition)
        element_desc = element_desc or self._get_element_description(locator)
        logging.debug(f"{self.__class__.__name__}: Right clicking element [ {element_desc}:{locator} ].")
        ActionChains(self.driver).context_click(element).perform()
        logging.info(f"{self.__class__.__name__}: Right clicked element [ {element_desc}:{locator} ] successfully.")

    def select_radio(self, locator, element_desc=None, condition="clickable"):
        element = self._resolve_element(locator, element_desc, condition)
        element_desc = element_desc or self._get_element_description(locator)
        logging.debug(f"{self.__class__.__name__}: Selecting radio button [ {element_desc}:{locator} ].")
        element.click()
        logging.info(f"{self.__class__.__name__}: Selected radio button [ {element_desc}:{locator} ] successfully.")

    def select_radio_by_value(self, locator, value, element_desc=None, condition="clickable"):
        formatted_locator = (locator[0], locator[1].format(value))
        element = self._resolve_element(formatted_locator, element_desc, condition)
        element_desc = element_desc or self._get_element_description(formatted_locator)
        logging.debug(f"{self.__class__.__name__}: Selecting radio button with value '{value}' in radio group [ {element_desc}:{formatted_locator} ].")
        element.click()
        logging.info(f"{self.__class__.__name__}: Selected radio button with value '{value}' in radio group [ {element_desc}:{formatted_locator} ] successfully.")

    def send_custom_key(self,locator, key='ENTER', element_desc=None, condition="clickable"):
        element = self._resolve_element(locator, element_desc, condition)
        element_desc = element_desc or self._get_element_description(locator)
        logging.debug(f"{self.__class__.__name__}: Sending custom key '{key}' to element [ {element_desc}:{locator} ] with ActionChains.")
        key_to_send = getattr(Keys, key.upper(), key)
        ActionChains(self.driver).send_keys_to_element(element, key_to_send).perform()
        logging.info(f"{self.__class__.__name__}: Sent custom key '{key}' to element [ {element_desc}:{locator} ] with ActionChains successfully.")