from selenium import webdriver
from selenium.webdriver.chrome.service import Service


class WebDriverFactory:
    @staticmethod
    def create_chrome_driver(chrome_path, chromedriver_path):
        options = webdriver.ChromeOptions()
        options.binary_location = chrome_path
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--remote-debugging-port=9222')
        service = Service(executable_path=chromedriver_path)
        return webdriver.Chrome(service=service, options=options)

    @staticmethod
    def quit_driver(driver):
        if driver:
            driver.quit()
