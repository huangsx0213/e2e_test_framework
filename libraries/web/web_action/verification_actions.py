from numpy import around
from selenium.common import NoSuchElementException, TimeoutException

from .base import Base
from .decorators import wait_and_perform
import logging

class VerificationActions(Base):
    @wait_and_perform(default_condition="presence")
    def element_text_should_be(self, element, expected_text):
        element_desc = self._get_element_description(element)
        logging.info(f"{self.__class__.__name__}: Checking if element text matches expected: {element_desc}, expected text: '{expected_text}'")
        actual_text = element.text
        assert actual_text == expected_text, f"{self.__class__.__name__}: Expected text: '{expected_text}' is not matching actual text: '{actual_text}'"
        logging.info(f"{self.__class__.__name__}: Element text matches expected: '{expected_text}', Actual text: '{actual_text}'")

    @wait_and_perform(default_condition="presence")
    def element_text_should_contains(self, element, expected_text):
        element_desc = self._get_element_description(element)
        logging.info(f"{self.__class__.__name__}: Checking if element text contains expected: {element_desc}, expected text: '{expected_text}'")
        actual_text = element.text
        assert expected_text in actual_text, f"{self.__class__.__name__}: Expected text: '{expected_text}' is not in actual text: '{actual_text}'"
        logging.info(f"{self.__class__.__name__}: Element text contains expected: '{expected_text}', Actual text: '{actual_text}'")

    def title_should_be(self, expected_title):
        logging.info(f"{self.__class__.__name__}: Checking if page title matches expected: '{expected_title}'")
        actual_title = self.driver.title
        assert actual_title == expected_title, f"{self.__class__.__name__}: Expected title: '{expected_title}' is not matching actual title: '{actual_title}'"
        logging.info(f"{self.__class__.__name__}: Title matches expected: '{expected_title}', Actual title: '{actual_title}'")

    def title_should_contains(self, expected_title):
        logging.info(f"{self.__class__.__name__}: Checking if page title contains expected: '{expected_title}'")
        actual_title = self.driver.title
        assert expected_title in actual_title, f"{self.__class__.__name__}: Expected title: '{expected_title}' is not in actual title: '{actual_title}'"
        logging.info(f"{self.__class__.__name__}: Title contains expected: '{expected_title}', Actual title: '{actual_title}'")


    def is_element_present(self, locator):
        logging.info(f"{self.__class__.__name__}: Checking if element is present: {locator}")
        try:
            element = self.driver.find_element(*locator)
            element_desc = self._get_element_description(element)
            logging.info(f"{self.__class__.__name__}: Element is present: {element_desc}")
            return True
        except NoSuchElementException:
            logging.info(f"{self.__class__.__name__}: Element is not present: {locator}")
            return False

    def is_element_visible(self, locator, timeout=None):
        logging.info(f"{self.__class__.__name__}: Checking if element is visible: {locator}, timeout: {timeout}")
        try:
            element = self.wait_for_element(locator, condition="visibility", timeout=timeout)
            element_desc = self._get_element_description(element)
            logging.info(f"{self.__class__.__name__}: Element is visible: {element_desc}")
            return True
        except TimeoutException:
            logging.info(f"{self.__class__.__name__}: Element is not visible: {locator}")
            return False

    def is_element_clickable(self, locator, timeout=None):
        logging.info(f"{self.__class__.__name__}: Checking if element is clickable: {locator}, timeout: {timeout}")
        try:
            element = self.wait_for_element(locator, condition="clickable", timeout=timeout)
            element_desc = self._get_element_description(element)
            logging.info(f"{self.__class__.__name__}: Element is clickable: {element_desc}")
            return True
        except TimeoutException:
            logging.info(f"{self.__class__.__name__}: Element is not clickable: {locator}")
            return False

    @wait_and_perform(default_condition="presence")
    def is_element_selected(self, element):
        element_desc = self._get_element_description(element)
        logging.info(f"{self.__class__.__name__}: Checking if element is selected: {element_desc}")
        is_selected = element.is_selected()
        logging.info(f"{self.__class__.__name__}: Element selected status: {is_selected} for element: {element_desc}")
        return is_selected

    @wait_and_perform(default_condition="presence")
    def is_element_enabled(self, element):
        element_desc = self._get_element_description(element)
        logging.info(f"{self.__class__.__name__}: Checking if element is enabled: {element_desc}")
        is_enabled = element.is_enabled()
        logging.info(f"{self.__class__.__name__}: Element enabled status: {is_enabled} for element: {element_desc}")
        return is_enabled


    @wait_and_perform(default_condition="presence")
    def capture_element_value(self, element, variable_name):
        element_desc = self._get_element_description(element)
        logging.info(f"{self.__class__.__name__}: Capturing value from element: {element_desc}")
        value = self.get_text(element)
        self.builtin.set_global_variable(f"${{{variable_name}}}", value)
        logging.info(f"{self.__class__.__name__}: Saved value '{value}' to variable ${{{variable_name}}}")
        return value

    @wait_and_perform(default_condition="presence")
    def assert_value_change(self, element, initial_value_variable, expected_change):
        element_desc = self._get_element_description(element)
        logging.info(f"{self.__class__.__name__}: Asserting value change for element: {element_desc}")

        initial_value = float(self.builtin.get_variable_value(f"${{{initial_value_variable}}}"))
        current_value = float(self.get_text(element))
        actual_change = around(current_value - initial_value, 2)
        expected_change = float(expected_change)

        logging.info(f"{self.__class__.__name__}: Actual diff: {actual_change}, Expected diff: {expected_change}")

        if not self._compare_diff(actual_change, expected_change):
            raise AssertionError(f"{self.__class__.__name__}: Dynamic check failed for element: {element_desc}")
