from selenium.webdriver import ActionChains
from selenium.webdriver.support.select import Select
import logging
from .base import Base


class ElementActions(Base):

    def send_keys(self, element, value, condition="presence"):
        element_desc = self._get_element_description(element)
        logging.info(f"{self.__class__.__name__}: Sending keys to element: {element_desc}")
        logging.info(f"{self.__class__.__name__}: Value to be sent: {value}")

        if isinstance(element, tuple):
            element = self.wait_for_element(element, condition=condition)

        element.send_keys(value)
        logging.info(f"{self.__class__.__name__}: Keys sent successfully to element: {element_desc}")

    def click(self, element, condition="clickable"):
        element_desc = self._get_element_description(element)
        logging.info(f"{self.__class__.__name__}: Clicking element: {element_desc}")

        if isinstance(element, tuple):
            element = self.wait_for_element(element, condition=condition)

        element.click()
        logging.info(f"{self.__class__.__name__}: Element clicked successfully: {element_desc}")

    def clear(self, element, condition="presence"):
        element_desc = self._get_element_description(element)
        logging.info(f"{self.__class__.__name__}: Clearing element: {element_desc}")

        if isinstance(element, tuple):
            element = self.wait_for_element(element, condition=condition)

        element.clear()
        logging.info(f"{self.__class__.__name__}: Element cleared successfully: {element_desc}")

    def get_text(self, element, condition="presence"):
        element_desc = self._get_element_description(element)
        logging.info(f"{self.__class__.__name__}: Getting text from element: {element_desc}")

        if isinstance(element, tuple):
            element = self.wait_for_element(element, condition=condition)

        text = element.text
        logging.info(f"{self.__class__.__name__}: Text retrieved: '{text}' from element: {element_desc}")
        return text

    def get_attribute(self, element, attribute_name, condition="presence"):
        element_desc = self._get_element_description(element)
        logging.info(f"{self.__class__.__name__}: Getting attribute '{attribute_name}' from element: {element_desc}")

        if isinstance(element, tuple):
            element = self.wait_for_element(element, condition=condition)

        attribute_value = element.get_attribute(attribute_name)
        logging.info(f"{self.__class__.__name__}: Attribute '{attribute_name}' value: '{attribute_value}' for element: {element_desc}")
        return attribute_value

    def select_by_value(self, element, value, condition="presence"):
        element_desc = self._get_element_description(element)
        logging.info(f"{self.__class__.__name__}: Selecting option by value: {value} for element: {element_desc}")

        if isinstance(element, tuple):
            element = self.wait_for_element(element, condition=condition)

        Select(element).select_by_value(value)
        logging.info(f"{self.__class__.__name__}: Option selected successfully: {value} for element: {element_desc}")

    def select_by_visible_text(self, element, text, condition="presence"):
        element_desc = self._get_element_description(element)
        logging.info(f"{self.__class__.__name__}: Selecting option by visible text: {text} for element: {element_desc}")

        if isinstance(element, tuple):
            element = self.wait_for_element(element, condition=condition)

        Select(element).select_by_visible_text(text)
        logging.info(f"{self.__class__.__name__}: Option selected successfully: {text} for element: {element_desc}")

    def select_by_index(self, element, index, condition="presence"):
        element_desc = self._get_element_description(element)
        logging.info(f"{self.__class__.__name__}: Selecting option by index: {index} for element: {element_desc}")

        if isinstance(element, tuple):
            element = self.wait_for_element(element, condition=condition)

        Select(element).select_by_index(int(index))
        logging.info(f"{self.__class__.__name__}: Option selected successfully at index: {index} for element: {element_desc}")

    def hover(self, element, condition="visibility"):
        element_desc = self._get_element_description(element)
        logging.info(f"{self.__class__.__name__}: Hovering over element: {element_desc}")

        if isinstance(element, tuple):
            element = self.wait_for_element(element, condition=condition)

        ActionChains(self.driver).move_to_element(element).perform()
        logging.info(f"{self.__class__.__name__}: Hovered over element successfully: {element_desc}")

    def double_click(self, element, condition="clickable"):
        element_desc = self._get_element_description(element)
        logging.info(f"{self.__class__.__name__}: Double clicking element: {element_desc}")

        if isinstance(element, tuple):
            element = self.wait_for_element(element, condition=condition)

        ActionChains(self.driver).double_click(element).perform()
        logging.info(f"{self.__class__.__name__}: Double clicked element successfully: {element_desc}")

    def right_click(self, element, condition="clickable"):
        element_desc = self._get_element_description(element)
        logging.info(f"{self.__class__.__name__}: Right clicking element: {element_desc}")

        if isinstance(element, tuple):
            element = self.wait_for_element(element, condition=condition)

        ActionChains(self.driver).context_click(element).perform()
        logging.info(f"{self.__class__.__name__}: Right clicked element successfully: {element_desc}")

    def scroll_into_view(self, element, condition="presence"):
        element_desc = self._get_element_description(element)
        logging.info(f"{self.__class__.__name__}: Scrolling element into view: {element_desc}")

        if isinstance(element, tuple):
            element = self.wait_for_element(element, condition=condition)

        self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
        logging.info(f"{self.__class__.__name__}: Scrolled element into view successfully: {element_desc}")

    def scroll_to_element(self, element, condition="presence"):
        element_desc = self._get_element_description(element)
        logging.info(f"{self.__class__.__name__}: Scrolling to element: {element_desc}")

        if isinstance(element, tuple):
            element = self.wait_for_element(element, condition=condition)

        self.driver.execute_script(
            "arguments[0].scrollIntoView({behavior: 'smooth', block: 'center', inline: 'nearest'});", element)
        logging.info(f"{self.__class__.__name__}: Scrolled to element successfully: {element_desc}")

    def select_radio(self, element, condition="clickable"):
        if isinstance(element, tuple):
            element = self.wait_for_element(element, condition=condition)
        element.click()

    def select_radio_by_value(self, element, value, condition="clickable"):
        logging.info(f"{self.__class__.__name__}: Selecting radio button with value '{value}' in radio group: {element}")
        locator_type, locator = element
        locator = locator.format(value)
        element = (locator_type, locator)

        element = self.wait_for_element(element, condition=condition)
        self.select_radio(element)
        logging.info(f"{self.__class__.__name__}: Selected radio button with value '{value}'")
