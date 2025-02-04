from numpy import around
from selenium.common import NoSuchElementException, TimeoutException
from robot.libraries.BuiltIn import BuiltIn
from .base import Base
import logging
from robot.api import logger
from libraries.common.log_manager import ColorLogger


class VerificationActions(Base):
    def verify_text_is(self, locator, expected_text, element_desc=None, condition="presence"):
        element = self._resolve_element(locator, element_desc, condition)
        element_desc = element_desc or self._get_element_description(locator)
        logging.debug(f"{self.__class__.__name__}: Checking if element text matches expected: {element_desc}, expected text: '{expected_text}'")
        actual_text = element.text
        result = actual_text == expected_text
        log_message = f"UI Verification: Asserting: {element_desc}, verify_text_is, Expected: {expected_text}, Actual: {actual_text}"
        self._log_result(result, log_message)
        assert result, f"{self.__class__.__name__}: Expected text: '{expected_text}' is not matching actual text: '{actual_text}'"

    def verify_figure_is(self, locator, expected_figure, element_desc=None, condition="presence"):
        element = self._resolve_element(locator, element_desc, condition)
        element_desc = element_desc or self._get_element_description(locator)
        logging.debug(f"{self.__class__.__name__}: Checking if element figure matches expected: {element_desc}, expected figure: '{expected_figure}'")
        try:
            expected_value = float(expected_figure.replace(",", "").strip())
        except Exception as e:
            logging.error(f"{self.__class__.__name__}: Error converting expected figure to float: {expected_figure}")
            raise e
        try:
            actual_value = float(element.text.replace(",", "").strip())
        except Exception as e:
            logging.error(f"{self.__class__.__name__}: Error converting actual figure to float from element text: {element.text}")
            raise e
        result = around(actual_value, decimals=2) == around(expected_value, decimals=2)
        log_message = f"UI Verification: Asserting: {element_desc}, verify_figure_is, Expected: {expected_value}, Actual: {actual_value}"
        self._log_result(result, log_message)
        assert result, f"{self.__class__.__name__}: Expected figure: '{expected_value}' is not matching actual figure: '{actual_value}'"

    def verify_text_contains(self, locator, expected_text, element_desc=None, condition="presence"):
        element = self._resolve_element(locator, element_desc, condition)
        element_desc = element_desc or self._get_element_description(locator)
        logging.debug(f"{self.__class__.__name__}: Checking if element text contains expected: {element_desc}, expected text: '{expected_text}'")
        actual_text = element.text
        result = expected_text in actual_text
        log_message = f"UI Verification: Asserting: {element_desc}, verify_text_contains, Expected: {expected_text}, Actual: {actual_text}"
        self._log_result(result, log_message)
        assert result, f"{self.__class__.__name__}: Expected text: '{expected_text}' is not in actual text: '{actual_text}'"

    def verify_figure_text_contains(self, locator, expected_text, element_desc=None, condition="presence"):
        element = self._resolve_element(locator, element_desc, condition)
        element_desc = element_desc or self._get_element_description(locator)
        logging.debug(f"{self.__class__.__name__}: Checking if element figure text contains expected: {element_desc}, expected text: '{expected_text}'")
        expected_text_clean = expected_text.replace(",", "").strip()
        actual_text_clean = element.text.replace(",", "").strip()
        result = expected_text_clean in actual_text_clean
        log_message = f"UI Verification: Asserting: {element_desc}, verify_figure_text_contains, Expected: {expected_text_clean}, Actual: {actual_text_clean}"
        self._log_result(result, log_message)
        assert result, f"{self.__class__.__name__}: Expected text: '{expected_text_clean}' is not in actual text: '{actual_text_clean}'"

    def verify_title_is(self, expected_title, element_desc="Page Title"):
        logging.debug(f"{self.__class__.__name__}: Checking if page title matches expected: '{expected_title}'")
        actual_title = self.driver.title
        result = actual_title == expected_title
        log_message = f"UI Verification: Asserting: {element_desc}, verify_title_is, Expected: {expected_title}, Actual: {actual_title}"
        self._log_result(result, log_message)
        assert result, f"{self.__class__.__name__}: Expected title: '{expected_title}' is not matching actual title: '{actual_title}'"

    def verify_title_contains(self, expected_title, element_desc="Page Title"):
        logging.debug(f"{self.__class__.__name__}: Checking if page title contains expected: '{expected_title}'")
        actual_title = self.driver.title
        result = expected_title in actual_title
        log_message = f"UI Verification: Asserting: {element_desc}, verify_title_contains, Expected: {expected_title}, Actual: {actual_title}"
        self._log_result(result, log_message)
        assert result, f"{self.__class__.__name__}: Expected title: '{expected_title}' is not in actual title: '{actual_title}'"

    def verify_element_exists(self, locator, element_desc=None):
        element_desc = element_desc or self._get_element_description(locator)
        logging.debug(f"{self.__class__.__name__}: Checking if element exists: {element_desc}")
        try:
            self._resolve_element(locator, element_desc, condition="presence")
            result = True
        except NoSuchElementException:
            result = False
        log_message = f"UI Verification: Asserting: {element_desc}, verify_element_exists, Expected: True, Actual: {result}"
        self._log_result(result, log_message)
        return result

    def verify_element_visible(self, locator, timeout=None, element_desc=None):
        element_desc = element_desc or self._get_element_description(locator)
        logging.debug(f"{self.__class__.__name__}: Checking if element is visible: {element_desc}, timeout: {timeout}")
        try:
            self.wait_for_element(locator, condition="visibility", timeout=timeout)
            result = True
        except TimeoutException:
            result = False
        log_message = f"UI Verification: Asserting: {element_desc}, verify_element_visible, Expected: True, Actual: {result}"
        self._log_result(result, log_message)
        return result

    def verify_element_invisible(self, locator, timeout=None, element_desc=None):
        element_desc = element_desc or self._get_element_description(locator)
        logging.debug(f"{self.__class__.__name__}: Checking if element is invisible: {element_desc}, timeout: {timeout}")
        try:
            self.wait_for_element(locator, condition="invisibility", timeout=timeout)
            result = True
        except TimeoutException:
            result = False
        log_message = f"UI Verification: Asserting: {element_desc}, verify_element_invisible, Expected: True, Actual: {result}"
        self._log_result(result, log_message)
        return result

    def verify_element_clickable(self, locator, timeout=None, element_desc=None):
        element_desc = element_desc or self._get_element_description(locator)
        logging.debug(f"{self.__class__.__name__}: Checking if element is clickable: {element_desc}, timeout: {timeout}")
        try:
            self.wait_for_element(locator, condition="clickable", timeout=timeout)
            result = True
        except TimeoutException:
            result = False
        log_message = f"UI Verification: Asserting: {element_desc}, verify_element_clickable, Expected: True, Actual: {result}"
        self._log_result(result, log_message)
        return result

    def verify_element_selected(self, locator, element_desc=None, condition="presence"):
        element = self._resolve_element(locator, element_desc, condition)
        element_desc = element_desc or self._get_element_description(locator)
        logging.debug(f"{self.__class__.__name__}: Checking if element is selected: {element_desc}")
        is_selected = element.is_selected()
        log_message = f"UI Verification: Asserting: {element_desc}, verify_element_selected, Expected: True, Actual: {is_selected}"
        self._log_result(is_selected, log_message)
        assert is_selected, f"{self.__class__.__name__}: Element {element_desc} is not selected as expected."
        return is_selected

    def verify_element_enabled(self, locator, element_desc=None, condition="presence"):
        element = self._resolve_element(locator, element_desc, condition)
        element_desc = element_desc or self._get_element_description(locator)
        logging.debug(f"{self.__class__.__name__}: Checking if element is enabled: {element_desc}")
        is_enabled = element.is_enabled()
        log_message = f"UI Verification: Asserting: {element_desc}, verify_element_enabled, Expected: True, Actual: {is_enabled}"
        self._log_result(is_enabled, log_message)
        assert is_enabled, f"{self.__class__.__name__}: Element {element_desc} is not enabled as expected."
        return is_enabled

    def get_text_save_to_variable(self, locator, variable_name, element_desc=None, condition="presence"):
        element = self._resolve_element(locator, element_desc, condition)
        element_desc = element_desc or self._get_element_description(locator)
        logging.debug(f"{self.__class__.__name__}: Capturing text from element: {element_desc}")
        value = element.text
        BuiltIn().set_global_variable(f"${{{variable_name}}}", value)
        logging.debug(f"{self.__class__.__name__}: Captured text: {value}")
        return value

    def verify_element_value_diff(self, locator, initial_value_variable, expected_change, element_desc=None, condition="presence"):
        element = self._resolve_element(locator, element_desc, condition)
        element_desc = element_desc or self._get_element_description(locator)
        logging.debug(f"{self.__class__.__name__}: Checking value difference for element: {element_desc}")
        initial_value = float(BuiltIn().get_variable_value(f"${{{initial_value_variable}}}"))
        current_value = float(element.text)
        actual_change = around(current_value - initial_value, decimals=2)
        expected_change_float = float(expected_change)
        result = self._compare_diff(actual_change, expected_change_float)
        log_message = f"UI Verification: Asserting: {element_desc}, verify_element_value_diff, Expected Change: {expected_change_float}, Actual Change: {actual_change}"
        self._log_result(result, log_message)
        assert result, f"{self.__class__.__name__}: Expected change: '{expected_change_float}' does not match actual change: '{actual_change}' for element {element_desc}"

    def _compare_diff(self, actual, expected):
        return around(actual, decimals=2) == around(expected, decimals=2)

    def _log_result(self, success: bool, message: str):
        """Logs the result of a check with appropriate color."""
        logging.debug(f"{self.__class__.__name__}: {message}")
        logger.info(
            ColorLogger.success(f"=> {message}") if success else ColorLogger.error(f"=> {message}"), html=True)
