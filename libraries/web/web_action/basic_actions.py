from selenium.webdriver import ActionChains
from selenium.webdriver.support.select import Select

from .base import Base
from .decorators import wait_and_perform
import logging

class BasicActions(Base):
    def open_url(self, url):
        logging.info(f"{self.__class__.__name__}: Opening URL: {url}")
        self.driver.maximize_window()
        self.driver.get(url)
        logging.info(f"{self.__class__.__name__}: URL opened successfully: {url}")

    @wait_and_perform(default_condition="presence")
    def send_keys(self, element, value):
        element_desc = self._get_element_description(element)
        logging.info(f"{self.__class__.__name__}: Sending keys to element: {element_desc}")
        logging.info(f"{self.__class__.__name__}: Value to be sent: {value}")
        element.send_keys(value)
        logging.info(f"{self.__class__.__name__}: Keys sent successfully to element: {element_desc}")

    @wait_and_perform(default_condition="clickable")
    def click(self, element):
        element_desc = self._get_element_description(element)
        logging.info(f"{self.__class__.__name__}: Clicking element: {element_desc}")
        element.click()
        logging.info(f"{self.__class__.__name__}: Element clicked successfully: {element_desc}")

    @wait_and_perform(default_condition="presence")
    def clear(self, element):
        element_desc = self._get_element_description(element)
        logging.info(f"{self.__class__.__name__}: Clearing element: {element_desc}")
        element.clear()
        logging.info(f"{self.__class__.__name__}: Element cleared successfully: {element_desc}")

    @wait_and_perform(default_condition="presence")
    def get_text(self, element):
        element_desc = self._get_element_description(element)
        logging.info(f"{self.__class__.__name__}: Getting text from element: {element_desc}")
        text = element.text
        logging.info(f"{self.__class__.__name__}: Text retrieved: '{text}' from element: {element_desc}")
        return text

    @wait_and_perform(default_condition="presence")
    def get_attribute(self, element, attribute_name):
        element_desc = self._get_element_description(element)
        logging.info(f"{self.__class__.__name__}: Getting attribute '{attribute_name}' from element: {element_desc}")
        attribute_value = element.get_attribute(attribute_name)
        logging.info(f"{self.__class__.__name__}: Attribute '{attribute_name}' value: '{attribute_value}' for element: {element_desc}")
        return attribute_value

    @wait_and_perform(default_condition="presence")
    def select_by_value(self, element, value):
        element_desc = self._get_element_description(element)
        logging.info(f"{self.__class__.__name__}: Selecting option by value: {value} for element: {element_desc}")
        Select(element).select_by_value(value)
        logging.info(f"{self.__class__.__name__}: Option selected successfully: {value} for element: {element_desc}")

    @wait_and_perform(default_condition="presence")
    def select_by_visible_text(self, element, text):
        element_desc = self._get_element_description(element)
        logging.info(f"{self.__class__.__name__}: Selecting option by visible text: {text} for element: {element_desc}")
        Select(element).select_by_visible_text(text)
        logging.info(f"{self.__class__.__name__}: Option selected successfully: {text} for element: {element_desc}")

    @wait_and_perform(default_condition="presence")
    def select_by_index(self, element, index):
        element_desc = self._get_element_description(element)
        logging.info(f"{self.__class__.__name__}: Selecting option by index: {index} for element: {element_desc}")
        Select(element).select_by_index(int(index))
        logging.info(
            f"{self.__class__.__name__}: Option selected successfully at index: {index} for element: {element_desc}")

    @wait_and_perform(default_condition="visibility")
    def hover(self, element):
        element_desc = self._get_element_description(element)
        logging.info(f"{self.__class__.__name__}: Hovering over element: {element_desc}")
        ActionChains(self.driver).move_to_element(element).perform()
        logging.info(f"{self.__class__.__name__}: Hovered over element successfully: {element_desc}")

    @wait_and_perform(default_condition="clickable")
    def double_click(self, element):
        element_desc = self._get_element_description(element)
        logging.info(f"{self.__class__.__name__}: Double clicking element: {element_desc}")
        ActionChains(self.driver).double_click(element).perform()
        logging.info(f"{self.__class__.__name__}: Double clicked element successfully: {element_desc}")

    @wait_and_perform(default_condition="clickable")
    def right_click(self, element):
        element_desc = self._get_element_description(element)
        logging.info(f"{self.__class__.__name__}: Right clicking element: {element_desc}")
        ActionChains(self.driver).context_click(element).perform()
        logging.info(f"{self.__class__.__name__}: Right clicked element successfully: {element_desc}")

    @wait_and_perform(default_condition="presence")
    def scroll_into_view(self, element):
        element_desc = self._get_element_description(element)
        logging.info(f"{self.__class__.__name__}: Scrolling element into view: {element_desc}")
        self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
        logging.info(f"{self.__class__.__name__}: Scrolled element into view successfully: {element_desc}")

    @wait_and_perform(default_condition="presence")
    def scroll_to_element(self, element):
        element_desc = self._get_element_description(element)
        logging.info(f"{self.__class__.__name__}: Scrolling to element: {element_desc}")
        self.driver.execute_script(
            "arguments[0].scrollIntoView({behavior: 'smooth', block: 'center', inline: 'nearest'});", element)
        logging.info(f"{self.__class__.__name__}: Scrolled to element successfully: {element_desc}")

    @wait_and_perform(default_condition="presence")
    def get_text(self, element):
        element_desc = self._get_element_description(element)
        logging.info(f"{self.__class__.__name__}: Getting text from element: {element_desc}")
        text = element.text
        logging.info(f"{self.__class__.__name__}: Text retrieved: '{text}' from element: {element_desc}")
        return text

    @wait_and_perform(default_condition="presence")
    def get_attribute(self, element, attribute_name):
        element_desc = self._get_element_description(element)
        logging.info(f"{self.__class__.__name__}: Getting attribute '{attribute_name}' from element: {element_desc}")
        attribute_value = element.get_attribute(attribute_name)
        logging.info(
            f"{self.__class__.__name__}: Attribute '{attribute_name}' value: '{attribute_value}' for element: {element_desc}")
        return attribute_value

    @wait_and_perform(default_condition="presence")
    def select_radio_by_value(self, element, value):
        element_desc = self._get_element_description(element)
        logging.info(f"{self.__class__.__name__}: Selecting radio button with value '{value}' in radio group: {element_desc}")

        radio_buttons = element

        for radio in radio_buttons:
            if radio.get_attribute("value") == value:
                if not radio.is_selected():
                    radio.click()
                logging.info(f"{self.__class__.__name__}: Radio button with value '{value}' selected successfully")
                return

    @wait_and_perform(default_condition="presence")
    def select_radio_by_text(self, element, text):
        element_desc = self._get_element_description(element)
        logging.info(f"{self.__class__.__name__}: Selecting radio button with text '{text}' in radio group: {element_desc}")

        radio_buttons = element

        for radio in radio_buttons:
            # 获取单选按钮的标签文本
            label = radio.find_element(By.XPATH, "./following-sibling::label[1]")
            if label.text.strip() == text:
                if not radio.is_selected():
                    radio.click()
                logging.info(f"{self.__class__.__name__}: Radio button with text '{text}' selected successfully")
                return