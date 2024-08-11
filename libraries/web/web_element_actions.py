import base64
import datetime
import logging
import time
from robot.libraries.BuiltIn import BuiltIn
from selenium.common import NoSuchElementException, TimeoutException
from selenium.webdriver import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.remote.webelement import WebElement
import io
from PIL import Image

class WebElementActions:
    def __init__(self, driver, default_timeout=10):
        self.driver = driver
        self.default_timeout = default_timeout

    def wait_for_element(self, locator, condition="presence", timeout=None):
        if timeout is None:
            timeout = self.default_timeout

        logging.info(f"{self.__class__.__name__}: Waiting for element with locator {locator}, condition: {condition}, timeout: {timeout}")
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

            logging.info(f"{self.__class__.__name__}: Element found successfully: {locator}")
            return result
        except TimeoutException:
            logging.error(f"{self.__class__.__name__}: Timeout waiting for element: {locator}, condition: {condition}")
            raise

    def open_url(self, url):
        logging.info(f"{self.__class__.__name__}: Opening URL: {url}")
        self.driver.maximize_window()
        self.driver.get(url)
        logging.info(f"{self.__class__.__name__}: URL opened successfully: {url}")

    def send_keys(self, element, value):
        element_desc = self._get_element_description(element)
        logging.info(f"{self.__class__.__name__}: Sending keys to element: {element_desc}, value: {value}")
        element.send_keys(value)
        logging.info(f"{self.__class__.__name__}: Keys sent successfully to element: {element_desc}")

    def click(self, element):
        element_desc = self._get_element_description(element)
        logging.info(f"{self.__class__.__name__}: Clicking element: {element_desc}")
        element.click()
        logging.info(f"{self.__class__.__name__}: Element clicked successfully: {element_desc}")

    def clear(self, element):
        element_desc = self._get_element_description(element)
        logging.info(f"{self.__class__.__name__}: Clearing element: {element_desc}")
        element.clear()
        logging.info(f"{self.__class__.__name__}: Element cleared successfully: {element_desc}")

    def select_by_value(self, element, value):
        element_desc = self._get_element_description(element)
        logging.info(f"{self.__class__.__name__}: Selecting option by value: {value} for element: {element_desc}")
        Select(element).select_by_value(value)
        logging.info(f"O{self.__class__.__name__}: Option selected successfully: {value} for element: {element_desc}")

    def select_by_visible_text(self, element, text):
        element_desc = self._get_element_description(element)
        logging.info(f"{self.__class__.__name__}: Selecting option by visible text: {text} for element: {element_desc}")
        Select(element).select_by_visible_text(text)
        logging.info(f"{self.__class__.__name__}: Option selected successfully: {text} for element: {element_desc}")

    def select_by_index(self, element, index):
        element_desc = self._get_element_description(element)
        logging.info(f"{self.__class__.__name__}: Selecting option by index: {index} for element: {element_desc}")
        Select(element).select_by_index(int(index))
        logging.info(f"{self.__class__.__name__}: Option selected successfully at index: {index} for element: {element_desc}")

    def hover(self, element):
        element_desc = self._get_element_description(element)
        logging.info(f"{self.__class__.__name__}: Hovering over element: {element_desc}")
        ActionChains(self.driver).move_to_element(element).perform()
        logging.info(f"{self.__class__.__name__}: Hovered over element successfully: {element_desc}")

    def double_click(self, element):
        element_desc = self._get_element_description(element)
        logging.info(f"{self.__class__.__name__}: Double clicking element: {element_desc}")
        ActionChains(self.driver).double_click(element).perform()
        logging.info(f"{self.__class__.__name__}: Double clicked element successfully: {element_desc}")

    def right_click(self, element):
        element_desc = self._get_element_description(element)
        logging.info(f"{self.__class__.__name__}: Right clicking element: {element_desc}")
        ActionChains(self.driver).context_click(element).perform()
        logging.info(f"{self.__class__.__name__}: Right clicked element successfully: {element_desc}")

    def scroll_into_view(self, element):
        element_desc = self._get_element_description(element)
        logging.info(f"{self.__class__.__name__}: Scrolling element into view: {element_desc}")
        self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
        logging.info(f"{self.__class__.__name__}: Scrolled element into view successfully: {element_desc}")

    def scroll_to_element(self, element):
        element_desc = self._get_element_description(element)
        logging.info(f"{self.__class__.__name__}: Scrolling to element: {element_desc}")
        self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center', inline: 'nearest'});", element)
        logging.info(f"{self.__class__.__name__}: Scrolled to element successfully: {element_desc}")

    def get_text(self, element):
        element_desc = self._get_element_description(element)
        logging.info(f"{self.__class__.__name__}: Getting text from element: {element_desc}")
        text = element.text
        logging.info(f"{self.__class__.__name__}: Text retrieved: {text} from element: {element_desc}")
        return text

    def get_attribute(self, element, attribute_name):
        element_desc = self._get_element_description(element)
        logging.info(f"{self.__class__.__name__}: Getting attribute '{attribute_name}' from element: {element_desc}")
        attribute_value = element.get_attribute(attribute_name)
        logging.info(f"{self.__class__.__name__}: Attribute '{attribute_name}' value: {attribute_value} for element: {element_desc}")
        return attribute_value

    def is_element_present(self, locator):
        logging.info(f"{self.__class__.__name__}: Checking if element is present: {locator}")
        try:
            self.driver.find_element(*locator)
            logging.info(f"{self.__class__.__name__}: Element is present: {locator}")
            return True
        except NoSuchElementException:
            logging.info(f"{self.__class__.__name__}: Element is not present: {locator}")
            return False

    def is_element_visible(self, locator, timeout=None):
        logging.info(f"{self.__class__.__name__}: Checking if element is visible: {locator}, timeout: {timeout}")
        try:
            self.wait_for_element(locator, condition="visibility", timeout=timeout)
            logging.info(f"{self.__class__.__name__}: Element is visible: {locator}")
            return True
        except TimeoutException:
            logging.info(f"{self.__class__.__name__}: Element is not visible: {locator}")
            return False

    def is_element_clickable(self, locator, timeout=None):
        logging.info(f"{self.__class__.__name__}: Checking if element is clickable: {locator}, timeout: {timeout}")
        try:
            self.wait_for_element(locator, condition="clickable", timeout=timeout)
            logging.info(f"{self.__class__.__name__}: Element is clickable: {locator}")
            return True
        except TimeoutException:
            logging.info(f"{self.__class__.__name__}: Element is not clickable: {locator}")
            return False

    def is_element_selected(self, element):
        element_desc = self._get_element_description(element)
        logging.info(f"{self.__class__.__name__}: Checking if element is selected: {element_desc}")
        is_selected = element.is_selected()
        logging.info(f"{self.__class__.__name__}: Element selected status: {is_selected} for element: {element_desc}")
        return is_selected

    def is_element_enabled(self, element):
        element_desc = self._get_element_description(element)
        logging.info(f"{self.__class__.__name__}: Checking if element is enabled: {element_desc}")
        is_enabled = element.is_enabled()
        logging.info(f"{self.__class__.__name__}: Element enabled status: {is_enabled} for element: {element_desc}")
        return is_enabled

    def element_text_should_be(self, element, expected_text):
        element_desc = self._get_element_description(element)
        logging.info(f"{self.__class__.__name__}: Checking if element text matches expected: {element_desc}, expected text: {expected_text}")
        actual_text = self.get_text(element)
        result = actual_text == expected_text
        logging.info(f"{self.__class__.__name__}: Text match result: {result}, Actual text: {actual_text} for element: {element_desc}")
        return result

    def element_text_should_contains(self, element, expected_text):
        element_desc = self._get_element_description(element)
        logging.info(f"{self.__class__.__name__}: Checking if element text contains expected: {element_desc}, expected text: {expected_text}")
        actual_text = self.get_text(element)
        result = expected_text in actual_text
        logging.info(f"{self.__class__.__name__}: Text contain result: {result}, Actual text: {actual_text} for element: {element_desc}")
        return result

    def title_should_be(self, expected_title):
        logging.info(f"{self.__class__.__name__}: Checking if page title matches expected: {expected_title}")
        actual_title = self.driver.title
        result = actual_title == expected_title
        logging.info(f"{self.__class__.__name__}: Title match result: {result}, Actual title: {actual_title}")
        return result

    def title_should_contains(self, expected_title):
        logging.info(f"{self.__class__.__name__}: Checking if page title contains expected: {expected_title}")
        actual_title = self.driver.title
        result = expected_title in actual_title
        logging.info(f"{self.__class__.__name__}: Title contain result: {result}, Actual title: {actual_title}")
        return result

    def wait_for_text_to_be_present(self, locator, text, timeout=None):
        if timeout is None:
            timeout = self.default_timeout
        logging.info(f"{self.__class__.__name__}: Waiting for text '{text}' to be present in element: {locator}, timeout: {timeout}")
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.text_to_be_present_in_element(locator, text)
            )
            logging.info(f"{self.__class__.__name__}: Text '{text}' is present in element: {locator}")
            return True
        except TimeoutException:
            logging.warning(f"{self.__class__.__name__}: Text '{text}' is not present in element: {locator} after {timeout} seconds")
            return False

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
        logging.info(f"{self.__class__.__name__}: Alert text retrieved: {alert_text}")
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
                logging.info(f"{self.__class__.__name__}: Screenshot captured successfully at: " + str(datetime.datetime.now()))
                BuiltIn().log(f'<img src="data:image/webp;base64,{encoded_string}" width="1440px">', html=True)
            else:
                logging.error(f"{self.__class__.__name__}: WebDriver is not initialized.")
        except Exception as e:
            logging.error(f"{self.__class__.__name__}: Failed to capture screenshot: {str(e)}")
            BuiltIn().log(f"{self.__class__.__name__}: Failed to capture screenshot: {str(e)}", level="ERROR")

    def highlight_element(self, element, duration=2, color="lightgreen", border="3px solid red"):
        element_desc = self._get_element_description(element)
        logging.info(f"{self.__class__.__name__}: Highlighting element: {element_desc}")

        def apply_style(s):
            self.driver.execute_script("arguments[0].setAttribute('style', arguments[1]);", element, s)

        original_style = element.get_attribute('style')

        for _ in range(int(duration)):
            apply_style(f"{self.__class__.__name__}: background: {color}; border: {border};")
            time.sleep(0.25)
            apply_style(original_style)
            time.sleep(0.25)

        logging.info(f"{self.__class__.__name__}: Finished highlighting element: {element_desc}")

    def _get_element_description(self, element):
        if isinstance(element, WebElement):
            tag_name = element.tag_name
            element_id = element.get_attribute('id')
            element_class = element.get_attribute('class')
            element_name = element.get_attribute('name')

            description = f"<{tag_name}"
            if element_id:
                description += f" id='{element_id}'"
            if element_class:
                description += f" class='{element_class}'"
            if element_name:
                description += f" name='{element_name}'"
            description += ">"

            return description
        elif isinstance(element, tuple):
            return str(element)
        else:
            return str(element)
