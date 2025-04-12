import logging
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from libraries.web.web_action.table_verifier import TableVerifier


class Base:
    def __init__(self, driver: WebDriver, default_timeout: int = 60):
        self.driver = driver
        self.default_timeout = default_timeout
        self.table_verifier = TableVerifier(self.driver)

    def _get_element_description(self, element):
        if isinstance(element, WebElement):
            tag_name = element.tag_name
            element_id = element.get_attribute('id')
            element_class = element.get_attribute('class')
            element_name = element.get_attribute('name')
            element_text = element.text[:30] if element.text else ''

            description = f"<{tag_name}"
            if element_id:
                description += f" id='{element_id}'"
            if element_class:
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

    def _resolve_element(self, element, element_desc, condition, timeout=None):
        """ 解析元素，若传入的是 locator 元组，则等待元素加载 """
        if isinstance(element, tuple):
            return self.wait_for_element(element, element_desc, condition=condition, timeout=timeout)
        return element

    def wait_for_element(self, locator, element_desc=None, condition="presence", timeout=None):
        if timeout is None:
            timeout = self.default_timeout

        logging.debug(f"{self.__class__.__name__}: Waiting for element {element_desc} with locator {locator}, condition: {condition}, timeout: {timeout}")
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

            element_desc = element_desc or self._get_element_description(result)
            logging.info(f"{self.__class__.__name__}: Element found {element_desc} with locator {locator}, condition: {condition}.")
            return result
        except TimeoutException:
            logging.error(f"{self.__class__.__name__}: Timeout waiting for element {element_desc} with locator {locator}, condition: {condition}, timeout: {timeout}")
            raise
