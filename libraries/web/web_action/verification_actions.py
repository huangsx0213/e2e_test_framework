from numpy import around
from selenium.common import NoSuchElementException, TimeoutException
from robot.libraries.BuiltIn import BuiltIn
from .base import Base
import logging


class VerificationActions(Base):
    def verify_text_is(self, element, expected_text, condition="presence"):
        element_desc = self._get_element_description(element)
        logging.info(f"{self.__class__.__name__}: Checking if element text matches expected: {element_desc}, expected text: '{expected_text}'")

        if isinstance(element, tuple):
            element = self.wait_for_element(element, condition=condition)

        actual_text = element.text
        assert actual_text == expected_text, f"{self.__class__.__name__}: Expected text: '{expected_text}' is not matching actual text: '{actual_text}'"
        logging.info(f"{self.__class__.__name__}: Element text matches expected: '{expected_text}', Actual text: '{actual_text}'")

    def verify_figure_is(self, element, expected_figure, condition="presence"):
        element_desc = self._get_element_description(element)
        logging.info(f"{self.__class__.__name__}: Checking if element figure matches expected: {element_desc}, expected figure: '{expected_figure}'")

        if isinstance(element, tuple):
            element = self.wait_for_element(element, condition=condition)

        expected_figure = float(expected_figure.replace(",", "").strip())
        actual_figure = float(element.text.replace(",", "").strip())
        assert around(actual_figure, decimals=2) == around(expected_figure, decimals=2), \
            f"{self.__class__.__name__}: Expected figure: '{expected_figure}' is not matching actual figure: '{actual_figure}'"
        logging.info(f"{self.__class__.__name__}: Element figure matches expected: '{expected_figure}', Actual figure: '{actual_figure}'")

    def verify_text_contains(self, element, expected_text, condition="presence"):
        element_desc = self._get_element_description(element)
        logging.info(f"{self.__class__.__name__}: Checking if element text contains expected: {element_desc}, expected text: '{expected_text}'")

        if isinstance(element, tuple):
            element = self.wait_for_element(element, condition=condition)

        actual_text = element.text
        assert expected_text in actual_text, f"{self.__class__.__name__}: Expected text: '{expected_text}' is not in actual text: '{actual_text}'"
        logging.info(f"{self.__class__.__name__}: Element text contains expected: '{expected_text}', Actual text: '{actual_text}'")

    def verify_figure_text_contains(self, element, expected_text, condition="presence"):
        element_desc = self._get_element_description(element)
        logging.info(f"{self.__class__.__name__}: Checking if element figure to text contains expected: {element_desc}, expected text: '{expected_text}'")

        if isinstance(element, tuple):
            element = self.wait_for_element(element, condition=condition)

        expected_text = expected_text.replace(",", "").strip()
        actual_text = element.text.replace(",", "").strip()
        assert expected_text in actual_text, f"{self.__class__.__name__}: Expected text: '{expected_text}' is not in actual text: '{actual_text}'"
        logging.info(f"{self.__class__.__name__}: Element text contains expected: '{expected_text}', Actual text: '{actual_text}'")

    def verify_title_is(self, expected_title):
        logging.info(f"{self.__class__.__name__}: Checking if page title matches expected: '{expected_title}'")
        actual_title = self.driver.title
        assert actual_title == expected_title, f"{self.__class__.__name__}: Expected title: '{expected_title}' is not matching actual title: '{actual_title}'"
        logging.info(f"{self.__class__.__name__}: Title matches expected: '{expected_title}', Actual title: '{actual_title}'")

    def verify_title_contains(self, expected_title):
        logging.info(f"{self.__class__.__name__}: Checking if page title contains expected: '{expected_title}'")
        actual_title = self.driver.title
        assert expected_title in actual_title, f"{self.__class__.__name__}: Expected title: '{expected_title}' is not in actual title: '{actual_title}'"
        logging.info(f"{self.__class__.__name__}: Title contains expected: '{expected_title}', Actual title: '{actual_title}'")

    def check_element_exists(self, locator):
        logging.info(f"{self.__class__.__name__}: Checking if element is present: {locator}")
        try:
            element = self.driver.find_element(*locator)
            element_desc = self._get_element_description(element)
            logging.info(f"{self.__class__.__name__}: Element exists: {element_desc}")
            return True
        except NoSuchElementException:
            logging.info(f"{self.__class__.__name__}: Element does not exist: {locator}")
            return False

    def check_element_visible(self, locator, timeout=None):
        logging.info(f"{self.__class__.__name__}: Checking if element is visible: {locator}, timeout: {timeout}")
        try:
            element = self.wait_for_element(locator, condition="visibility", timeout=timeout)
            element_desc = self._get_element_description(element)
            logging.info(f"{self.__class__.__name__}: Element is visible: {element_desc}")
            return True
        except TimeoutException:
            logging.info(f"{self.__class__.__name__}: Element is not visible: {locator}")
            return False

    def check_element_invisible(self, locator, timeout=None):
        logging.info(f"{self.__class__.__name__}: Checking if element is invisible: {locator}, timeout: {timeout}")
        try:
            element = self.wait_for_element(locator, condition="invisibility", timeout=timeout)
            element_desc = self._get_element_description(element)
            logging.info(f"{self.__class__.__name__}: Element is invisible: {element_desc}")
            return True
        except TimeoutException:
            logging.info(f"{self.__class__.__name__}: Element is not invisible: {locator}")
            return False

    def check_element_clickable(self, locator, timeout=None):
        logging.info(f"{self.__class__.__name__}: Checking if element is clickable: {locator}, timeout: {timeout}")
        try:
            element = self.wait_for_element(locator, condition="clickable", timeout=timeout)
            element_desc = self._get_element_description(element)
            logging.info(f"{self.__class__.__name__}: Element is clickable: {element_desc}")
            return True
        except TimeoutException:
            logging.info(f"{self.__class__.__name__}: Element is not clickable: {locator}")
            return False

    def check_element_selected(self, element, condition="presence"):
        element_desc = self._get_element_description(element)
        logging.info(f"{self.__class__.__name__}: Checking if element is selected: {element_desc}")

        if isinstance(element, tuple):
            element = self.wait_for_element(element, condition=condition)

        is_selected = element.is_selected()
        logging.info(f"{self.__class__.__name__}: Element selected status: {is_selected} for element: {element_desc}")
        return is_selected

    def check_element_enabled(self, element, condition="presence"):
        element_desc = self._get_element_description(element)
        logging.info(f"{self.__class__.__name__}: Checking if element is enabled: {element_desc}")

        if isinstance(element, tuple):
            element = self.wait_for_element(element, condition=condition)

        is_enabled = element.is_enabled()
        logging.info(f"{self.__class__.__name__}: Element enabled status: {is_enabled} for element: {element_desc}")
        return is_enabled

    def get_text_save_to_variable(self, element, variable_name, condition="presence"):
        element_desc = self._get_element_description(element)
        logging.info(f"{self.__class__.__name__}: Capturing value from element: {element_desc}")

        if isinstance(element, tuple):
            element = self.wait_for_element(element, condition=condition)

        value = element.text
        BuiltIn().set_global_variable(f"${{{variable_name}}}", value)
        logging.info(f"{self.__class__.__name__}: Saved value '{value}' to variable ${{{variable_name}}}")
        return value

    def verify_value_changed_by(self, element, initial_value_variable, expected_change, condition="presence"):
        element_desc = self._get_element_description(element)
        logging.info(f"{self.__class__.__name__}: Asserting value change for element: {element_desc}")

        if isinstance(element, tuple):
            element = self.wait_for_element(element, condition=condition)

        initial_value = float(BuiltIn().get_variable_value(f"${{{initial_value_variable}}}"))
        current_value = float(element.text)
        actual_change = around(current_value - initial_value, 2)
        expected_change = float(expected_change)

        logging.info(f"{self.__class__.__name__}: Actual change: {actual_change}, Expected change: {expected_change}")

        if not self._compare_diff(actual_change, expected_change):
            raise AssertionError(f"{self.__class__.__name__}: Value change verification failed for element: {element_desc}")


    def _compare_diff(self, actual, expected):
        return around(actual, decimals=2) == around(expected, decimals=2)