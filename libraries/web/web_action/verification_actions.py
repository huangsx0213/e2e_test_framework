from numpy import around
from selenium.common import NoSuchElementException, TimeoutException
from robot.libraries.BuiltIn import BuiltIn
from .base import Base
import logging

class VerificationActions(Base):
    def verify_text_is(self, element, expected_text, element_name=None, condition="presence"):
        element_desc = self._get_element_description(element)
        logging.info(f"{self.__class__.__name__}: Checking if element text matches expected: {element_desc}, expected text: '{expected_text}'")

        if isinstance(element, tuple):
            element = self.wait_for_element(element, condition=condition)

        actual_text = element.text
        result = actual_text == expected_text
        log_message = f"UI Verification: Asserting: {element_name}, {self.__class__.verify_text_is.__name__}, Expected: {expected_text}, Actual: {actual_text}"
        logging.info(log_message)
        assert result, f"{self.__class__.__name__}: Expected text: '{expected_text}' is not matching actual text: '{actual_text}'"

    def verify_figure_is(self, element, expected_figure, element_name=None, condition="presence"):
        element_desc = self._get_element_description(element)
        logging.info(f"{self.__class__.__name__}: Checking if element figure matches expected: {element_desc}, expected figure: '{expected_figure}'")

        if isinstance(element, tuple):
            element = self.wait_for_element(element, condition=condition)

        expected_figure = float(expected_figure.replace(",", "").strip())
        actual_figure = float(element.text.replace(",", "").strip())
        result = around(actual_figure, decimals=2) == around(expected_figure, decimals=2)
        log_message = f"UI Verification: Asserting: {element_name}, {self.__class__.verify_figure_is.__name__}, Expected: {expected_figure}, Actual: {actual_figure}"
        logging.info(log_message)
        assert result, f"{self.__class__.__name__}: Expected figure: '{expected_figure}' is not matching actual figure: '{actual_figure}'"

    def verify_text_contains(self, element, expected_text, element_name=None, condition="presence"):
        element_desc = self._get_element_description(element)
        logging.info(f"{self.__class__.__name__}: Checking if element text contains expected: {element_desc}, expected text: '{expected_text}'")

        if isinstance(element, tuple):
            element = self.wait_for_element(element, condition=condition)

        actual_text = element.text
        result = expected_text in actual_text
        log_message = f"UI Verification: Asserting: {element_name}, {self.__class__.verify_text_contains.__name__}, Expected: {expected_text}, Actual: {actual_text}"
        logging.info(log_message)
        assert result, f"{self.__class__.__name__}: Expected text: '{expected_text}' is not in actual text: '{actual_text}'"

    def verify_figure_text_contains(self, element, expected_text, element_name=None, condition="presence"):
        element_desc = self._get_element_description(element)
        logging.info(f"{self.__class__.__name__}: Checking if element figure to text contains expected: {element_desc}, expected text: '{expected_text}'")

        if isinstance(element, tuple):
            element = self.wait_for_element(element, condition=condition)

        expected_text = expected_text.replace(",", "").strip()
        actual_text = element.text.replace(",", "").strip()
        result = expected_text in actual_text
        log_message = f"UI Verification: Asserting: {element_name}, {self.__class__.verify_figure_text_contains.__name__}, Expected: {expected_text}, Actual: {actual_text}"
        logging.info(log_message)
        assert result, f"{self.__class__.__name__}: Expected text: '{expected_text}' is not in actual text: '{actual_text}'"

    def verify_title_is(self, expected_title, element_name=None):
        logging.info(f"{self.__class__.__name__}: Checking if page title matches expected: '{expected_title}'")
        actual_title = self.driver.title
        result = actual_title == expected_title
        log_message = f"UI Verification: Asserting: {element_name}, {self.__class__.verify_title_is.__name__}, Expected: {expected_title}, Actual: {actual_title}"
        logging.info(log_message)
        assert result, f"{self.__class__.__name__}: Expected title: '{expected_title}' is not matching actual title: '{actual_title}'"

    def verify_title_contains(self, expected_title, element_name=None):
        logging.info(f"{self.__class__.__name__}: Checking if page title contains expected: '{expected_title}'")
        actual_title = self.driver.title
        result = expected_title in actual_title
        log_message = f"UI Verification: Asserting: {element_name}, {self.__class__.verify_title_contains.__name__}, Expected: {expected_title}, Actual: {actual_title}"
        logging.info(log_message)
        assert result, f"{self.__class__.__name__}: Expected title: '{expected_title}' is not in actual title: '{actual_title}'"

    def verify_element_exists(self, locator, element_name=None):
        logging.info(f"{self.__class__.__name__}: Checking if element is present: {locator}")
        try:
            element = self.driver.find_element(*locator)
            log_message = f"UI Verification: Asserting: {element_name}, {self.__class__.check_element_exists.__name__}, Expected: True, Actual: True"
            logging.info(log_message)
            return True
        except NoSuchElementException:
            log_message = f"UI Verification: Asserting: {element_name}, {self.__class__.check_element_exists.__name__}, Expected: True, Actual: False"
            logging.info(log_message)
            return False

    def verify_element_visible(self, locator, timeout=None, element_name=None):
        logging.info(f"{self.__class__.__name__}: Checking if element is visible: {locator}, timeout: {timeout}")
        try:
            element = self.wait_for_element(locator, condition="visibility", timeout=timeout)
            log_message = f"UI Verification: Asserting: {element_name}, {self.__class__.check_element_visible.__name__}, Expected: True, Actual: True"
            logging.info(log_message)
            return True
        except TimeoutException:
            log_message = f"UI Verification: Asserting: {element_name}, {self.__class__.check_element_visible.__name__}, Expected: True, Actual: False"
            logging.info(log_message)
            return False

    def verify_element_invisible(self, locator, timeout=None, element_name=None):
        logging.info(f"{self.__class__.__name__}: Checking if element is invisible: {locator}, timeout: {timeout}")
        try:
            element = self.wait_for_element(locator, condition="invisibility", timeout=timeout)
            log_message = f"UI Verification: Asserting: {element_name}, {self.__class__.check_element_invisible.__name__}, Expected: True, Actual: True"
            logging.info(log_message)
            return True
        except TimeoutException:
            log_message = f"UI Verification: Asserting: {element_name}, {self.__class__.check_element_invisible.__name__}, Expected: True, Actual: False"
            logging.info(log_message)
            return False

    def verify_element_clickable(self, locator, timeout=None, element_name=None):
        logging.info(f"{self.__class__.__name__}: Checking if element is clickable: {locator}, timeout: {timeout}")
        try:
            element = self.wait_for_element(locator, condition="clickable", timeout=timeout)
            log_message = f"UI Verification: Asserting: {element_name}, {self.__class__.check_element_clickable.__name__}, Expected: True, Actual: True"
            logging.info(log_message)
            return True
        except TimeoutException:
            log_message = f"UI Verification: Asserting: {element_name}, {self.__class__.check_element_clickable.__name__}, Expected: True, Actual: False"
            logging.info(log_message)
            return False

    def verify_element_selected(self, element,  element_name=None, condition="presence"):
        element_desc = self._get_element_description(element)
        logging.info(f"{self.__class__.__name__}: Checking if element is selected: {element_desc}")

        if isinstance(element, tuple):
            element = self.wait_for_element(element, condition=condition)

        is_selected = element.is_selected()
        log_message = f"UI Verification: Asserting: {element_name}, {self.__class__.check_element_selected.__name__}, Expected: True, Actual: {is_selected}"
        logging.info(log_message)
        return is_selected

    def verify_element_enabled(self, element, element_name=None, condition="presence"):
        element_desc = self._get_element_description(element)
        logging.info(f"{self.__class__.__name__}: Checking if element is enabled: {element_desc}")

        if isinstance(element, tuple):
            element = self.wait_for_element(element, condition=condition)

        is_enabled = element.is_enabled()
        log_message = f"UI Verification: Asserting: {element_name}, {self.__class__.check_element_enabled.__name__}, Expected: True, Actual: {is_enabled}"
        logging.info(log_message)
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

    def verify_element_value_diff(self, element, initial_value_variable, expected_change, condition="presence", element_name=None):
        element_desc = self._get_element_description(element)
        logging.info(f"{self.__class__.__name__}: Asserting value change for element: {element_desc}")

        if isinstance(element, tuple):
            element = self.wait_for_element(element, condition=condition)

        initial_value = float(BuiltIn().get_variable_value(f"${{{initial_value_variable}}}"))
        current_value = float(element.text)
        actual_change = around(current_value - initial_value, 2)
        expected_change = float(expected_change)

        result = self._compare_diff(actual_change, expected_change)
        log_message = f"UI Verification: Asserting: {element_name}, {self.__class__.verify_value_changed_by.__name__}, Expected: {expected_change}, Actual: {actual_change}"
        logging.info(log_message)

        if not result:
            raise AssertionError(f"{self.__class__.__name__}: Value change verification failed for element: {element_desc}")

    def _compare_diff(self, actual, expected):
        return around(actual, decimals=2) == around(expected, decimals=2)