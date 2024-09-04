import base64
import datetime
import logging
import time
import io
from PIL import Image
from typing import List, Dict, Union
from functools import wraps

from numpy.ma.core import around
from robot.libraries.BuiltIn import BuiltIn
from selenium.common import NoSuchElementException, TimeoutException
from selenium.webdriver import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.remote.webelement import WebElement
from libraries.web.table_verifier import TableVerifier


def wait_and_perform(default_condition="presence"):
    def decorator(func):
        @wraps(func)
        def wrapper(self, locator, *args, condition=None, **kwargs):
            used_condition = condition or default_condition
            if isinstance(locator, tuple):
                element = self.wait_for_element(locator, condition=used_condition)
            else:
                element = locator
            return func(self, element, *args, **kwargs)

        return wrapper

    return decorator


class WebElementActions:
    def __init__(self, driver, default_timeout=60):
        self.driver = driver
        self.default_timeout = default_timeout
        self.table_verifier = TableVerifier(self.driver)

    def _get_element_description(self, element):
        if isinstance(element, WebElement):
            tag_name = element.tag_name
            element_id = element.get_attribute('id')
            element_class = element.get_attribute('class')
            element_name = element.get_attribute('name')
            element_text = element.text[:30] if element.text else ''  # 获取前30个字符的文本

            description = f"<{tag_name}"
            if element_id:
                description += f" id='{element_id}'"
            if element_class:
                # 如果class很长，只显示前两个类名
                classes = element_class.split()
                if len(classes) > 2:
                    description += f" class='{' '.join(classes[:2])}...'"
                else:
                    description += f" class='{element_class}'"
            if element_name:
                description += f" name='{element_name}'"
            description += ">"
            if element_text:
                description += f" text='{element_text}...'"

            return description
        elif isinstance(element, tuple):
            return f"locator: {element}"
        else:
            return str(element)

    def wait_for_element(self, locator, condition="presence", timeout=None):
        if timeout is None:
            timeout = self.default_timeout

        logging.info(
            f"{self.__class__.__name__}: Waiting for element with locator {locator}, condition: {condition}, timeout: {timeout}")
        wait = WebDriverWait(self.driver, timeout)

        try:
            if condition == "presence":
                result = wait.until(EC.presence_of_element_located(locator))
            elif condition == "visibility":
                result = wait.until(EC.visibility_of_element_located(locator))
            elif condition == "clickable":
                result = wait.until(EC.element_to_be_clickable(locator))
            elif condition == "invisibility":
                result = wait.until(EC.invisibility_of_element_located(locator))
            else:
                raise ValueError(f"{self.__class__.__name__}: Unsupported condition: {condition}")

            element_desc = self._get_element_description(result)
            logging.info(f"{self.__class__.__name__}: Element found successfully: {element_desc}")
            return result
        except TimeoutException:
            logging.error(f"{self.__class__.__name__}: Timeout waiting for element: {locator}, condition: {condition}")
            raise

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

    def wait_for_element_present(self, locator, timeout=None):
        logging.info(f"{self.__class__.__name__}: Waiting for element to be present: {locator}")
        return self.wait_for_element(locator, condition="presence", timeout=timeout)

    def wait_for_element_visible(self, locator, timeout=None):
        logging.info(f"{self.__class__.__name__}: Waiting for element to be visible: {locator}")
        return self.wait_for_element(locator, condition="visibility", timeout=timeout)

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

    def wait_for_element_to_disappear(self, locator, timeout=None):
        if timeout is None:
            timeout = self.default_timeout
        logging.info(f"{self.__class__.__name__}: Waiting for element to disappear: {locator}, timeout: {timeout}")
        try:
            self.wait_for_element(locator, condition="invisibility", timeout=timeout)
            logging.info(f"{self.__class__.__name__}: Element disappeared: {locator}")
            return True
        except TimeoutException:
            logging.warning(f"{self.__class__.__name__}: Element did not disappear: {locator} after {timeout} seconds")
            return False

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

    @wait_and_perform(default_condition="presence")
    def switch_to_frame(self, element):
        element_desc = self._get_element_description(element)
        logging.info(f"{self.__class__.__name__}: Switching to frame: {element_desc}")
        self.driver.switch_to.frame(element)
        logging.info(f"{self.__class__.__name__}: Switched to frame successfully: {element_desc}")

    def switch_to_default_content(self):
        logging.info(f"{self.__class__.__name__}: Switching to default content")
        self.driver.switch_to.default_content()
        logging.info(f"{self.__class__.__name__}: Switched to default content successfully")

    def execute_script(self, script, *args):
        logging.info(f"{self.__class__.__name__}: Executing JavaScript: {script}, Arguments: {args}")
        result = self.driver.execute_script(script, *args)
        logging.info(f"{self.__class__.__name__}: JavaScript executed successfully, Result: {result}")
        return result

    def accept_alert(self):
        logging.info(f"{self.__class__.__name__}: Accepting alert")
        self.driver.switch_to.alert.accept()
        logging.info(f"{self.__class__.__name__}: Alert accepted successfully")

    def dismiss_alert(self):
        logging.info(f"{self.__class__.__name__}: Dismissing alert")
        self.driver.switch_to.alert.dismiss()
        logging.info(f"{self.__class__.__name__}: Alert dismissed successfully")

    def get_alert_text(self):
        logging.info(f"{self.__class__.__name__}: Getting alert text")
        alert_text = self.driver.switch_to.alert.text
        logging.info(f"{self.__class__.__name__}: Alert text retrieved: '{alert_text}'")
        return alert_text

    def capture_screenshot(self):
        try:
            if self.driver:
                # Capture the screenshot as binary PNG image
                screenshot_binary = self.driver.get_screenshot_as_png()

                # Open the image using PIL
                image = Image.open(io.BytesIO(screenshot_binary))

                # Resize the image
                base_width = 1440
                w_percent = (base_width / float(image.size[0]))
                h_size = int((float(image.size[1]) * float(w_percent)))
                image = image.resize((base_width, h_size), Image.LANCZOS)

                # Convert the image to WebP format and compress
                buffer = io.BytesIO()
                image.save(buffer, format="WebP", quality=30)

                # Encode the compressed image as base64
                encoded_string = base64.b64encode(buffer.getvalue()).decode('utf-8')
                logging.info(
                    f"{self.__class__.__name__}: Screenshot captured successfully at: " + str(datetime.datetime.now()))
                BuiltIn().log(f'<img src="data:image/webp;base64,{encoded_string}" width="1440px">', html=True)
            else:
                logging.error(f"{self.__class__.__name__}: WebDriver is not initialized.")
        except Exception as e:
            logging.error(f"{self.__class__.__name__}: Failed to capture screenshot: {str(e)}")
            BuiltIn().log(f"{self.__class__.__name__}: Failed to capture screenshot: {str(e)}", level="ERROR")

    @wait_and_perform(default_condition="visibility")
    def highlight_element(self, element, duration=2, color="lightgreen", border="3px solid red"):
        element_desc = self._get_element_description(element)
        logging.info(f"{self.__class__.__name__}: Highlighting element: {element_desc}")

        def apply_style(s):
            self.driver.execute_script("arguments[0].setAttribute('style', arguments[1]);", element, s)

        original_style = element.get_attribute('style')

        for _ in range(int(duration)):
            apply_style(f"background: {color}; border: {border};")
            time.sleep(0.25)
            apply_style(original_style)
            time.sleep(0.25)

        logging.info(f"{self.__class__.__name__}: Finished highlighting element: {element_desc}")

    def verify_table_exact(self, table_locator: Union[tuple, WebElement], expected_data: List[Dict[str, str]]):
        logging.info(f"{self.__class__.__name__}: Verifying entire table with exact match")
        table_element = self.wait_for_element(table_locator) if isinstance(table_locator, tuple) else table_locator
        table_desc = self._get_element_description(table_element)
        self.table_verifier.verify_table(table_element, expected_data, match_type='exact')
        logging.info(f"{self.__class__.__name__}: Table verification (exact match) completed for table: {table_desc}")

    def verify_table_row_exact(self, table_locator: Union[tuple, WebElement], row_index: int,
                               expected_data: Dict[str, str]):
        logging.info(f"{self.__class__.__name__}: Verifying table row at index {row_index} with exact match")
        table_element = self.wait_for_element(table_locator) if isinstance(table_locator, tuple) else table_locator
        table_desc = self._get_element_description(table_element)
        self.table_verifier.verify_table_row(table_element, row_index, expected_data, match_type='exact')
        logging.info(f"{self.__class__.__name__}: Table row verification (exact match) completed for table: {table_desc}, row: {row_index}")

    def verify_specific_cell_exact(self, table_locator: Union[tuple, WebElement], row_index: int,
                                   column: Union[str, int], expected_value: str):
        logging.info(f"{self.__class__.__name__}: Verifying specific cell at row {row_index}, column {column} with exact match")
        table_element = self.wait_for_element(table_locator) if isinstance(table_locator, tuple) else table_locator
        table_desc = self._get_element_description(table_element)
        self.table_verifier.verify_specific_cell(table_element, row_index, column, expected_value, match_type='exact')
        logging.info(f"{self.__class__.__name__}: Specific cell verification (exact match) completed for table: {table_desc}, row: {row_index}, column: {column}")

    def verify_table_partial(self, table_locator: Union[tuple, WebElement], expected_data: List[Dict[str, str]]):
        logging.info(f"{self.__class__.__name__}: Verifying entire table with partial match")
        table_element = self.wait_for_element(table_locator) if isinstance(table_locator, tuple) else table_locator
        table_desc = self._get_element_description(table_element)
        self.table_verifier.verify_table(table_element, expected_data, match_type='partial')
        logging.info(f"{self.__class__.__name__}: Table verification (partial match) completed for table: {table_desc}")

    def verify_table_row_partial(self, table_locator: Union[tuple, WebElement], row_index: int,
                                 expected_data: Dict[str, str]):
        logging.info(f"{self.__class__.__name__}: Verifying table row at index {row_index} with partial match")
        table_element = self.wait_for_element(table_locator) if isinstance(table_locator, tuple) else table_locator
        table_desc = self._get_element_description(table_element)
        self.table_verifier.verify_table_row(table_element, row_index, expected_data, match_type='partial')
        logging.info(f"{self.__class__.__name__}: Table row verification (partial match) completed for table: {table_desc}, row: {row_index}")

    def verify_specific_cell_partial(self, table_locator: Union[tuple, WebElement], row_index: int,
                                     column: Union[str, int], expected_value: str):
        logging.info(f"{self.__class__.__name__}: Verifying specific cell at row {row_index}, column {column} with partial match")
        table_element = self.wait_for_element(table_locator) if isinstance(table_locator, tuple) else table_locator
        table_desc = self._get_element_description(table_element)
        self.table_verifier.verify_specific_cell(table_element, row_index, column, expected_value, match_type='partial')
        logging.info(f"{self.__class__.__name__}: Specific cell verification (partial match) completed for table: {table_desc}, row: {row_index}, column: {column}")

    def verify_table_regex(self, table_locator: Union[tuple, WebElement], expected_data: List[Dict[str, str]]):
        logging.info(f"{self.__class__.__name__}: Verifying entire table with regex match")
        table_element = self.wait_for_element(table_locator) if isinstance(table_locator, tuple) else table_locator
        table_desc = self._get_element_description(table_element)
        self.table_verifier.verify_table(table_element, expected_data, match_type='regex')
        logging.info(f"{self.__class__.__name__}: Table verification (regex match) completed for table: {table_desc}")

    def verify_table_row_regex(self, table_locator: Union[tuple, WebElement], row_index: int, expected_data: Dict[str, str]):
        logging.info(f"{self.__class__.__name__}: Verifying table row at index {row_index} with regex match")
        table_element = self.wait_for_element(table_locator) if isinstance(table_locator, tuple) else table_locator
        table_desc = self._get_element_description(table_element)
        self.table_verifier.verify_table_row(table_element, row_index, expected_data, match_type='regex')
        logging.info(f"{self.__class__.__name__}: Table row verification (regex match) completed for table: {table_desc}, row: {row_index}")

    def verify_specific_cell_regex(self, table_locator: Union[tuple, WebElement], row_index: int, column: Union[str, int], expected_value: str):
        logging.info(f"{self.__class__.__name__}: Verifying specific cell at row {row_index}, column {column} with regex match")
        table_element = self.wait_for_element(table_locator) if isinstance(table_locator, tuple) else table_locator
        table_desc = self._get_element_description(table_element)
        self.table_verifier.verify_specific_cell(table_element, row_index, column, expected_value, match_type='regex')
        logging.info(f"{self.__class__.__name__}: Specific cell verification (regex match) completed for table: {table_desc}, row: {row_index}, column: {column}")

    def select_table_row_checkbox(self, table_locator: Union[tuple, WebElement], identifier_column: Union[str, int], identifier_value: str, checkbox_column: int = 1):
        logging.info(f"{self.__class__.__name__}: Selecting checkbox for row with {identifier_column}: {identifier_value}")
        try:
            table_element = self.wait_for_element(table_locator) if isinstance(table_locator, tuple) else table_locator
            table_desc = self._get_element_description(table_element)
            self.table_verifier.select_table_row_checkbox(table_element, identifier_column, identifier_value, checkbox_column)
            logging.info(f"{self.__class__.__name__}: Checkbox selected successfully for row with {identifier_column}: {identifier_value} in table: {table_desc}")
        except Exception as e:
            logging.error(f"{self.__class__.__name__}: Error selecting checkbox: {str(e)}")
            raise

    def select_multiple_table_row_checkboxes(self, table_locator: Union[tuple, WebElement], identifier_column: Union[str, int], identifier_values: List[str],
                                             checkbox_column: int = 1):
        logging.info(f"{self.__class__.__name__}: Selecting checkboxes for multiple rows with {identifier_column}: {identifier_values}")
        try:
            table_element = self.wait_for_element(table_locator) if isinstance(table_locator, tuple) else table_locator
            table_desc = self._get_element_description(table_element)
            self.table_verifier.select_multiple_table_row_checkboxes(table_element, identifier_column, identifier_values,
                                                                     checkbox_column)
            logging.info(f"{self.__class__.__name__}: Checkboxes selected successfully for rows with {identifier_column}: {identifier_values} in table: {table_desc}")
        except Exception as e:
            logging.error(f"{self.__class__.__name__}: Error selecting multiple checkboxes: {str(e)}")
            raise

    def verify_table_is_empty(self, table_locator: Union[tuple, WebElement]):
        logging.info(f"{self.__class__.__name__}: Verifying table is empty")
        try:
            table_element = self.wait_for_element(table_locator) if isinstance(table_locator, tuple) else table_locator
            table_desc = self._get_element_description(table_element)
            self.table_verifier.verify_table_is_empty(table_element)
            logging.info(f"{self.__class__.__name__}: Table empty verification completed successfully for table: {table_desc}")
        except Exception as e:
            logging.error(f"{self.__class__.__name__}: Error verifying table is empty: {str(e)}")
            raise

    def verify_unique_column_values(self, table_locator: Union[tuple, WebElement], column: Union[str, int]):
        logging.info(f"{self.__class__.__name__}: Verifying unique values in column: {column}")
        try:
            table_element = self.wait_for_element(table_locator) if isinstance(table_locator, tuple) else table_locator
            table_desc = self._get_element_description(table_element)
            self.table_verifier.verify_unique_column_values(table_element, column)
            logging.info(f"{self.__class__.__name__}: Unique column values verification completed successfully for table: {table_desc}, column: {column}")
        except Exception as e:
            logging.error(f"{self.__class__.__name__}: Error verifying unique column values: {str(e)}")
            raise

    def verify_value_in_table(self, table_locator: Union[tuple, WebElement], search_value: str):
        logging.info(f"{self.__class__.__name__}: Verifying value '{search_value}' exists in table")
        try:
            table_element = self.wait_for_element(table_locator) if isinstance(table_locator, tuple) else table_locator
            table_desc = self._get_element_description(table_element)
            result = self.table_verifier.verify_value_in_table(table_element, search_value)
            logging.info(f"{self.__class__.__name__}: Value verification in table completed successfully for table: {table_desc}")
            return result
        except Exception as e:
            logging.error(f"{self.__class__.__name__}: Error verifying value in table: {str(e)}")
            raise

    def verify_row_count(self, table_locator: Union[tuple, WebElement], expected_row_count: int):
        logging.info(f"{self.__class__.__name__}: Verifying row count: expected {expected_row_count}")
        try:
            table_element = self.wait_for_element(table_locator) if isinstance(table_locator, tuple) else table_locator
            table_desc = self._get_element_description(table_element)
            self.table_verifier.verify_row_count(table_element, expected_row_count)
            logging.info(f"{self.__class__.__name__}: Row count verification completed successfully for table: {table_desc}")
        except Exception as e:
            logging.error(f"{self.__class__.__name__}: Error verifying row count: {str(e)}")
            raise

    def verify_column_sorted(self, table_locator: Union[tuple, WebElement], column: Union[str, int], expected_order='ascending', strip_spaces=True):
        logging.info(f"{self.__class__.__name__}: Verifying column '{column}' is sorted in {expected_order} order")
        try:
            table_element = self.wait_for_element(table_locator) if isinstance(table_locator, tuple) else table_locator
            table_desc = self._get_element_description(table_element)
            self.table_verifier.verify_column_sorted(table_element, column, expected_order, strip_spaces)
            logging.info(f"{self.__class__.__name__}: Column sorting verification completed successfully for table: {table_desc}, column: {column}")
        except Exception as e:
            logging.error(f"{self.__class__.__name__}: Error verifying column sorting: {str(e)}")
            raise

    def wait(self, seconds):
        logging.info(f"{self.__class__.__name__}: Waiting for {seconds} seconds")
        time.sleep(int(seconds))

    @wait_and_perform(default_condition="visibility")
    def get_element_size(self, element):
        element_desc = self._get_element_description(element)
        logging.info(f"{self.__class__.__name__}: Getting size of element: {element_desc}")
        size = element.size
        logging.info(f"{self.__class__.__name__}: Element size retrieved: {size} for element: {element_desc}")
        return size

    @wait_and_perform(default_condition="visibility")
    def get_element_location(self, element):
        element_desc = self._get_element_description(element)
        logging.info(f"{self.__class__.__name__}: Getting location of element: {element_desc}")
        location = element.location
        logging.info(f"{self.__class__.__name__}: Element location retrieved: {location} for element: {element_desc}")
        return location

    @wait_and_perform(default_condition="presence")
    def get_css_value(self, element, property_name):
        element_desc = self._get_element_description(element)
        logging.info(f"{self.__class__.__name__}: Getting CSS value of property '{property_name}' for element: {element_desc}")
        value = element.value_of_css_property(property_name)
        logging.info(f"{self.__class__.__name__}: CSS value retrieved: '{value}' for property '{property_name}' of element: {element_desc}")
        return value

    def switch_to_window(self, window_handle):
        logging.info(f"{self.__class__.__name__}: Switching to window with handle: {window_handle}")
        self.driver.switch_to.window(window_handle)
        logging.info(f"{self.__class__.__name__}: Switched to window successfully")

    def get_window_handles(self):
        logging.info(f"{self.__class__.__name__}: Getting all window handles")
        handles = self.driver.window_handles
        logging.info(f"{self.__class__.__name__}: Retrieved {len(handles)} window handles")
        return handles

    def close_current_window(self):
        logging.info(f"{self.__class__.__name__}: Closing current window")
        self.driver.close()
        logging.info(f"{self.__class__.__name__}: Current window closed successfully")

    def refresh_page(self):
        logging.info(f"{self.__class__.__name__}: Refreshing the current page")
        self.driver.refresh()
        logging.info(f"{self.__class__.__name__}: Page refreshed successfully")

    def go_back(self):
        logging.info(f"{self.__class__.__name__}: Navigating back in browser history")
        self.driver.back()
        logging.info(f"{self.__class__.__name__}: Navigated back successfully")

    def go_forward(self):
        logging.info(f"{self.__class__.__name__}: Navigating forward in browser history")
        self.driver.forward()
        logging.info(f"{self.__class__.__name__}: Navigated forward successfully")

    def get_current_url(self):
        logging.info(f"{self.__class__.__name__}: Getting current URL")
        url = self.driver.current_url
        logging.info(f"{self.__class__.__name__}: Current URL is: '{url}'")
        return url

    def execute_async_script(self, script, *args):
        logging.info(f"{self.__class__.__name__}: Executing asynchronous JavaScript: {script}, Arguments: {args}")
        result = self.driver.execute_async_script(script, *args)
        logging.info(f"{self.__class__.__name__}: Asynchronous JavaScript executed successfully, Result: {result}")
        return result

    @wait_and_perform(default_condition="presence")
    def get_property(self, element, property_name):
        element_desc = self._get_element_description(element)
        logging.info(f"{self.__class__.__name__}: Getting property '{property_name}' for element: {element_desc}")
        value = element.get_property(property_name)
        logging.info(f"{self.__class__.__name__}: Property value retrieved: '{value}' for property '{property_name}' of element: {element_desc}")
        return value

    def set_window_size(self, width, height):
        logging.info(f"{self.__class__.__name__}: Setting window size to {width}x{height}")
        self.driver.set_window_size(width, height)
        logging.info(f"{self.__class__.__name__}: Window size set successfully")

    def maximize_window(self):
        logging.info(f"{self.__class__.__name__}: Maximizing window")
        self.driver.maximize_window()
        logging.info(f"{self.__class__.__name__}: Window maximized successfully")

    def minimize_window(self):
        logging.info(f"{self.__class__.__name__}: Minimizing window")
        self.driver.minimize_window()
        logging.info(f"{self.__class__.__name__}: Window minimized successfully")

    def fullscreen_window(self):
        logging.info(f"{self.__class__.__name__}: Setting window to full screen")
        self.driver.fullscreen_window()
        logging.info(f"{self.__class__.__name__}: Window set to full screen successfully")

    @wait_and_perform(default_condition="presence")
    def get_accessible_name(self, element):
        element_desc = self._get_element_description(element)
        logging.info(f"{self.__class__.__name__}: Getting accessible name for element: {element_desc}")
        name = element.accessible_name
        logging.info(f"{self.__class__.__name__}: Accessible name retrieved: '{name}' for element: {element_desc}")
        return name

    @wait_and_perform(default_condition="presence")
    def get_aria_role(self, element):
        element_desc = self._get_element_description(element)
        logging.info(f"{self.__class__.__name__}: Getting ARIA role for element: {element_desc}")
        role = element.aria_role
        logging.info(f"{self.__class__.__name__}: ARIA role retrieved: '{role}' for element: {element_desc}")
        return role

    def add_cookie(self, cookie_dict):
        logging.info(f"{self.__class__.__name__}: Adding cookie: {cookie_dict}")
        self.driver.add_cookie(cookie_dict)
        logging.info(f"{self.__class__.__name__}: Cookie added successfully")

    def get_cookie(self, name):
        logging.info(f"{self.__class__.__name__}: Getting cookie with name: '{name}'")
        cookie = self.driver.get_cookie(name)
        logging.info(f"{self.__class__.__name__}: Cookie retrieved: {cookie}")
        return cookie

    def delete_cookie(self, name):
        logging.info(f"{self.__class__.__name__}: Deleting cookie with name: '{name}'")
        self.driver.delete_cookie(name)
        logging.info(f"{self.__class__.__name__}: Cookie deleted successfully")

    def delete_all_cookies(self):
        logging.info(f"{self.__class__.__name__}: Deleting all cookies")
        self.driver.delete_all_cookies()
        logging.info(f"{self.__class__.__name__}: All cookies deleted successfully")

    def get_log(self, log_type):
        logging.info(f"{self.__class__.__name__}: Getting logs of type: '{log_type}'")
        logs = self.driver.get_log(log_type)
        logging.info(f"{self.__class__.__name__}: Retrieved {len(logs)} log entries")
        return logs

    @wait_and_perform(default_condition="clickable")
    def js_click(self, element):
        element_desc = self._get_element_description(element)
        logging.info(f"{self.__class__.__name__}: Clicking element using JavaScript: {element_desc}")
        self.driver.execute_script("arguments[0].click();", element)
        logging.info(f"{self.__class__.__name__}: Element clicked successfully using JavaScript: {element_desc}")

    @wait_and_perform(default_condition="presence")
    def js_send_keys(self, element, value):
        element_desc = self._get_element_description(element)
        logging.info(f"{self.__class__.__name__}: Sending keys to element using JavaScript: {element_desc}")
        self.driver.execute_script(f"arguments[0].value = '{value}';", element)
        logging.info(f"{self.__class__.__name__}: Keys sent successfully using JavaScript: {element_desc}")

    @wait_and_perform(default_condition="presence")
    def js_clear(self, element):
        element_desc = self._get_element_description(element)
        logging.info(f"{self.__class__.__name__}: Clearing element using JavaScript: {element_desc}")
        self.driver.execute_script("arguments[0].value = '';", element)
        logging.info(f"{self.__class__.__name__}: Element cleared successfully using JavaScript: {element_desc}")

    @wait_and_perform(default_condition="presence")
    def js_scroll_into_view(self, element):
        element_desc = self._get_element_description(element)
        logging.info(f"{self.__class__.__name__}: Scrolling element into view using JavaScript: {element_desc}")
        self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
        logging.info(f"{self.__class__.__name__}: Element scrolled into view successfully using JavaScript: {element_desc}")

    @wait_and_perform(default_condition="presence")
    def js_select_option(self, select_element, option_text):
        element_desc = self._get_element_description(select_element)
        logging.info(f"{self.__class__.__name__}: Selecting option '{option_text}' using JavaScript: {element_desc}")
        self.driver.execute_script(
            "var select = arguments[0];"
            "for(var i = 0; i < select.options.length; i++) {"
            "  if(select.options[i].text == arguments[1]) {"
            "    select.options[i].selected = true;"
            "    var event = new Event('change', { bubbles: true });"
            "    select.dispatchEvent(event);"
            "    break;"
            "  }"
            "}", select_element, option_text
        )
        logging.info(f"{self.__class__.__name__}: Option selected successfully using JavaScript: {element_desc}")

    @wait_and_perform(default_condition="visibility")
    def js_hover(self, element):
        element_desc = self._get_element_description(element)
        logging.info(f"{self.__class__.__name__}: Hovering over element using JavaScript: {element_desc}")
        self.driver.execute_script(
            "var event = new MouseEvent('mouseover', {"
            "  'view': window,"
            "  'bubbles': true,"
            "  'cancelable': true"
            "});"
            "arguments[0].dispatchEvent(event);", element
        )
        logging.info(f"{self.__class__.__name__}: Hovered over element successfully using JavaScript: {element_desc}")

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

    def _compare_diff(self, actual_diff: float, expected_diff: str) -> bool:
        expected_operator = expected_diff[0]
        expected_value = float(expected_diff[1:])

        if expected_operator == '+':
            return actual_diff == expected_value
        elif expected_operator == '-':
            return actual_diff == -expected_value
        else:
            raise ValueError(f"{self.__class__.__name__}: Unsupported operator in expected diff: {expected_operator}")
