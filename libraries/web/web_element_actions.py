from selenium.common import NoSuchElementException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.remote.webelement import WebElement
from libraries.common.log_manager import logger


class WebElementActions:
    def __init__(self, driver, default_timeout=10):
        self.driver = driver
        self.default_timeout = default_timeout

    def wait_for_element(self, locator, condition="presence", timeout=None, element=None):
        if timeout is None:
            timeout = self.default_timeout

        logger.info(f"Waiting for element with locator {locator}, condition: {condition}, timeout: {timeout}")
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
                raise ValueError(f"Unsupported condition: {condition}")

            logger.info(f"Element found successfully: {locator}")
            return result
        except TimeoutException:
            logger.error(f"Timeout waiting for element: {locator}, condition: {condition}")
            raise

    def open_url(self, url):
        logger.info(f"Opening URL: {url}")
        self.driver.maximize_window()
        self.driver.get(url)
        logger.info(f"URL opened successfully: {url}")

    def send_keys(self, element, value):
        element_desc = self._get_element_description(element)
        logger.info(f"Sending keys to element: {element_desc}, value: {value}")
        element.send_keys(value)
        logger.info(f"Keys sent successfully to element: {element_desc}")

    def click(self, element):
        element_desc = self._get_element_description(element)
        logger.info(f"Clicking element: {element_desc}")
        element.click()
        logger.info(f"Element clicked successfully: {element_desc}")

    def clear(self, element):
        element_desc = self._get_element_description(element)
        logger.info(f"Clearing element: {element_desc}")
        element.clear()
        logger.info(f"Element cleared successfully: {element_desc}")

    def select_by_value(self, element, value):
        element_desc = self._get_element_description(element)
        logger.info(f"Selecting option by value: {value} for element: {element_desc}")
        Select(element).select_by_value(value)
        logger.info(f"Option selected successfully: {value} for element: {element_desc}")

    def select_by_visible_text(self, element, text):
        element_desc = self._get_element_description(element)
        logger.info(f"Selecting option by visible text: {text} for element: {element_desc}")
        Select(element).select_by_visible_text(text)
        logger.info(f"Option selected successfully: {text} for element: {element_desc}")

    def select_by_index(self, element, index):
        element_desc = self._get_element_description(element)
        logger.info(f"Selecting option by index: {index} for element: {element_desc}")
        Select(element).select_by_index(int(index))
        logger.info(f"Option selected successfully at index: {index} for element: {element_desc}")

    def get_text(self, element):
        element_desc = self._get_element_description(element)
        logger.info(f"Getting text from element: {element_desc}")
        text = element.text
        logger.info(f"Text retrieved: {text} from element: {element_desc}")
        return text

    def get_attribute(self, element, attribute_name):
        element_desc = self._get_element_description(element)
        logger.info(f"Getting attribute '{attribute_name}' from element: {element_desc}")
        attribute_value = element.get_attribute(attribute_name)
        logger.info(f"Attribute '{attribute_name}' value: {attribute_value} for element: {element_desc}")
        return attribute_value

    def is_element_present(self, locator):
        logger.info(f"Checking if element is present: {locator}")
        try:
            self.driver.find_element(*locator)
            logger.info(f"Element is present: {locator}")
            return True
        except NoSuchElementException:
            logger.info(f"Element is not present: {locator}")
            return False

    def is_element_visible(self, locator, timeout=None):
        logger.info(f"Checking if element is visible: {locator}, timeout: {timeout}")
        try:
            self.wait_for_element(locator, condition="visibility", timeout=timeout)
            logger.info(f"Element is visible: {locator}")
            return True
        except TimeoutException:
            logger.info(f"Element is not visible: {locator}")
            return False

    def is_element_clickable(self, locator, timeout=None):
        logger.info(f"Checking if element is clickable: {locator}, timeout: {timeout}")
        try:
            self.wait_for_element(locator, condition="clickable", timeout=timeout)
            logger.info(f"Element is clickable: {locator}")
            return True
        except TimeoutException:
            logger.info(f"Element is not clickable: {locator}")
            return False

    def is_element_selected(self, element):
        element_desc = self._get_element_description(element)
        logger.info(f"Checking if element is selected: {element_desc}")
        is_selected = element.is_selected()
        logger.info(f"Element selected status: {is_selected} for element: {element_desc}")
        return is_selected

    def is_element_enabled(self, element):
        element_desc = self._get_element_description(element)
        logger.info(f"Checking if element is enabled: {element_desc}")
        is_enabled = element.is_enabled()
        logger.info(f"Element enabled status: {is_enabled} for element: {element_desc}")
        return is_enabled

    def element_text_should_be(self, element, expected_text):
        element_desc = self._get_element_description(element)
        logger.info(f"Checking if element text matches expected: {element_desc}, expected text: {expected_text}")
        actual_text = self.get_text(element)
        result = actual_text == expected_text
        logger.info(f"Text match result: {result}, Actual text: {actual_text} for element: {element_desc}")
        return result

    def element_text_should_contains(self, element, expected_text):
        element_desc = self._get_element_description(element)
        logger.info(f"Checking if element text contains expected: {element_desc}, expected text: {expected_text}")
        actual_text = self.get_text(element)
        result = expected_text in actual_text
        logger.info(f"Text contain result: {result}, Actual text: {actual_text} for element: {element_desc}")
        return result

    def title_should_be(self, expected_title):
        logger.info(f"Checking if page title matches expected: {expected_title}")
        actual_title = self.driver.title
        result = actual_title == expected_title
        logger.info(f"Title match result: {result}, Actual title: {actual_title}")
        return result

    def title_should_contains(self, expected_title):
        logger.info(f"Checking if page title contains expected: {expected_title}")
        actual_title = self.driver.title
        result = expected_title in actual_title
        logger.info(f"Title contain result: {result}, Actual title: {actual_title}")
        return result

    def switch_to_frame(self, element):
        element_desc = self._get_element_description(element)
        logger.info(f"Switching to frame: {element_desc}")
        self.driver.switch_to.frame(element)
        logger.info(f"Switched to frame successfully: {element_desc}")

    def switch_to_default_content(self):
        logger.info("Switching to default content")
        self.driver.switch_to.default_content()
        logger.info("Switched to default content successfully")

    def execute_script(self, script, *args):
        logger.info(f"Executing JavaScript: {script}, Arguments: {args}")
        result = self.driver.execute_script(script, *args)
        logger.info(f"JavaScript executed successfully, Result: {result}")
        return result

    def accept_alert(self):
        logger.info("Accepting alert")
        self.driver.switch_to.alert.accept()
        logger.info("Alert accepted successfully")

    def dismiss_alert(self):
        logger.info("Dismissing alert")
        self.driver.switch_to.alert.dismiss()
        logger.info("Alert dismissed successfully")

    def get_alert_text(self):
        logger.info("Getting alert text")
        alert_text = self.driver.switch_to.alert.text
        logger.info(f"Alert text retrieved: {alert_text}")
        return alert_text

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
