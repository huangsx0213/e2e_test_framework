from selenium.common import NoSuchElementException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select


class WebElementActions:
    def __init__(self, driver, default_timeout=10):
        self.driver = driver
        self.default_timeout = default_timeout

    def wait_for_element(self, locator, condition="presence", timeout=None, element=None):
        if timeout is None:
            timeout = self.default_timeout

        wait = WebDriverWait(self.driver, timeout)

        if condition == "presence":
            return wait.until(EC.presence_of_element_located(locator))
        elif condition == "visibility":
            return wait.until(EC.visibility_of_element_located(locator))
        elif condition == "clickable":
            return wait.until(EC.element_to_be_clickable(locator))
        elif condition == "invisibility":
            return wait.until(EC.invisibility_of_element_located(locator))
        else:
            raise ValueError(f"Unsupported condition: {condition}")

    def open_url(self, url):
        self.driver.maximize_window()
        self.driver.get(url)

    def send_keys(self, element, value):
        element.send_keys(value)

    def click(self, element):
        element.click()

    def clear(self, element):
        element.clear()

    def select_by_value(self, element, value):
        Select(element).select_by_value(value)

    def select_by_visible_text(self, element, text):
        Select(element).select_by_visible_text(text)

    def select_by_index(self, element, index):
        Select(element).select_by_index(int(index))

    def get_text(self, element):
        return element.text

    def get_attribute(self, element, attribute_name):
        return element.get_attribute(attribute_name)

    def is_element_present(self, locator):
        try:
            self.driver.find_element(*locator)
            return True
        except NoSuchElementException:
            return False

    def is_element_visible(self, locator, timeout=None):
        try:
            self.wait_for_element(locator, condition="visibility", timeout=timeout)
            return True
        except TimeoutException:
            return False

    def is_element_clickable(self, locator, timeout=None):
        try:
            self.wait_for_element(locator, condition="clickable", timeout=timeout)
            return True
        except TimeoutException:
            return False

    def is_element_selected(self, element):
        return element.is_selected()

    def is_element_enabled(self, element):
        return element.is_enabled()

    def element_text_should_be(self, element, expected_text):
        actual_text = self.get_text(element)
        return actual_text == expected_text

    def element_text_should_contains(self, element, expected_text):
        actual_text = self.get_text(element)
        return expected_text in actual_text

    def title_should_be(self, expected_title):
        actual_title = self.driver.title
        return actual_title == expected_title

    def title_should_contains(self, expected_title):
        actual_title = self.driver.title
        return expected_title in actual_title

    def switch_to_frame(self, element):
        self.driver.switch_to.frame(element)

    def switch_to_default_content(self):
        self.driver.switch_to.default_content()

    def execute_script(self, script, *args):
        self.driver.execute_script(script, *args)
