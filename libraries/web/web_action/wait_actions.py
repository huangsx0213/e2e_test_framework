from .base import Base
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import logging
import time


class WaitActions(Base):
    def wait_for_element_present(self, locator, timeout=None):
        logging.info(f"{self.__class__.__name__}: Waiting for element to be present: {locator}")
        return self.wait_for_element(locator, condition="presence", timeout=timeout)

    def wait_for_element_visible(self, locator, timeout=None):
        logging.info(f"{self.__class__.__name__}: Waiting for element to be visible: {locator}")
        return self.wait_for_element(locator, condition="visibility", timeout=timeout)

    def wait_for_element_invisible(self, locator, timeout=None):
        logging.info(f"{self.__class__.__name__}: Waiting for element to be invisible: {locator}")
        return self.wait_for_element(locator, condition="invisibility", timeout=timeout)

    def wait_for_element_clickable(self, locator, timeout=None):
        logging.info(f"{self.__class__.__name__}: Waiting for element to be clickable: {locator}")
        return self.wait_for_element(locator, condition="clickable", timeout=timeout)

    def wait_for_text_present_in_element(self, locator, text, timeout=None):
        if timeout is None:
            timeout = self.default_timeout
        logging.info(f"{self.__class__.__name__}: Waiting for text '{text}' to be present in element: {locator}")
        try:
            wait = WebDriverWait(self.driver, timeout)
            element = wait.until(EC.text_to_be_present_in_element(locator, text))
            element_desc = self._get_element_description(element)
            logging.info(f"{self.__class__.__name__}: Text '{text}' is present in element: {element_desc}")
            return element
        except TimeoutException:
            logging.error(f"{self.__class__.__name__}: Text '{text}' not present in element: {locator}")
            raise

    def wait_for_staleness_of(self, element, timeout=None):
        if timeout is None:
            timeout = self.default_timeout
        element_desc = self._get_element_description(element)
        logging.info(f"{self.__class__.__name__}: Waiting for staleness of element: {element_desc}")
        try:
            wait = WebDriverWait(self.driver, timeout)
            wait.until(EC.staleness_of(element))
            logging.info(f"{self.__class__.__name__}: Element is stale: {element_desc}")
            return True
        except TimeoutException:
            logging.error(f"{self.__class__.__name__}: Element not stale: {element_desc}")
            return False

    def wait(self, seconds):
        logging.info(f"{self.__class__.__name__}: Waiting for {seconds} seconds")
        time.sleep(int(seconds))
