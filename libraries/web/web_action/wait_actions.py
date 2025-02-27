from .base import Base
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from robot.api.deco import keyword, library
import logging
import time

@library
class WaitActions(Base):
    ROBOT_LIBRARY_SCOPE = 'TEST SUITE'

    @keyword
    def wait_for_element_present(self, locator, element_desc=None, timeout=None):
        """
        Waits until the element is present in the DOM.
        """
        element_desc = element_desc or self._get_element_description(locator)
        logging.info(f"{self.__class__.__name__}: Waiting for element to be present: [ {element_desc}:{locator} ].")
        element = self._resolve_element(locator, element_desc, condition="presence", timeout=timeout)
        return element

    @keyword
    def wait_for_element_visible(self, locator, element_desc=None, timeout=None):
        """
        Waits until the element is visible on the page.
        """
        element_desc = element_desc or self._get_element_description(locator)
        logging.info(f"{self.__class__.__name__}: Waiting for element to be visible: [ {element_desc}:{locator} ].")
        element = self._resolve_element(locator, element_desc, condition="visibility", timeout=timeout)
        return element

    @keyword
    def wait_for_element_clickable(self, locator, element_desc=None, timeout=None):
        """
        Waits until the element is clickable.
        """
        element_desc = element_desc or self._get_element_description(locator)
        logging.info(f"{self.__class__.__name__}: Waiting for element to be clickable: [ {element_desc}:{locator} ].")
        element = self._resolve_element(locator, element_desc, condition="clickable", timeout=timeout)
        return element

    @keyword
    def wait_for_element_invisible(self, locator, element_desc=None, timeout=None):
        """
        Waits until the element becomes invisible.
        Note: This expected condition returns a boolean.
        """
        element_desc = element_desc or self._get_element_description(locator)
        logging.info(f"{self.__class__.__name__}: Waiting for element to become invisible: [ {element_desc}:{locator} ].")
        if timeout is None:
            timeout = self.default_timeout
        wait = WebDriverWait(self.driver, timeout)
        try:
            result = wait.until(EC.invisibility_of_element_located(locator))
            logging.info(f"{self.__class__.__name__}: Element is now invisible: [ {element_desc}:{locator} ].")
            return result
        except TimeoutException:
            logging.error(f"{self.__class__.__name__}: Timeout waiting for element to become invisible: [ {element_desc}:{locator} ].")
            raise

    @keyword
    def wait_for_text_present_in_element(self, locator, text, element_desc=None, timeout=None):
        """
        Waits until the given text is present in the specified element.
        """
        element_desc = element_desc or self._get_element_description(locator)
        logging.info(f"{self.__class__.__name__}: Waiting for text '{text}' to be present in element: [ {element_desc}:{locator} ].")
        if timeout is None:
            timeout = self.default_timeout
        wait = WebDriverWait(self.driver, timeout)
        try:
            result = wait.until(EC.text_to_be_present_in_element(locator, text))
            element = self.driver.find_element(*locator)
            element_desc = self._get_element_description(element)
            logging.info(f"{self.__class__.__name__}: Text '{text}' is present in element: [ {element_desc}:{locator} ].")
            return element
        except TimeoutException:
            logging.error(f"{self.__class__.__name__}: Timeout waiting for text '{text}' in element: [ {element_desc}:{locator} ].")
            raise

    @keyword
    def wait_for_staleness_of(self, element, timeout=None):
        """
        Waits until the element is no longer attached to the DOM.
        """
        element_desc = self._get_element_description(element)
        logging.info(f"{self.__class__.__name__}: Waiting for staleness of element: [ {element_desc} ].")
        if timeout is None:
            timeout = self.default_timeout
        wait = WebDriverWait(self.driver, timeout)
        try:
            wait.until(EC.staleness_of(element))
            logging.info(f"{self.__class__.__name__}: Element is stale: [ {element_desc} ].")
            return True
        except TimeoutException:
            logging.error(f"{self.__class__.__name__}: Timeout waiting for element to become stale: [ {element_desc} ].")
            return False

    @keyword
    def wait(self, seconds):
        """
        Pauses execution for the given number of seconds.
        """
        logging.info(f"{self.__class__.__name__}: Waiting for {seconds} seconds.")
        time.sleep(int(seconds))
