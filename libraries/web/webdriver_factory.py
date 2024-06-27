from selenium import webdriver
from selenium.webdriver.chrome.service import Service


class WebDriverFactory:
    @staticmethod
    def create_chrome_driver(chrome_path, chromedriver_path):
        options = webdriver.ChromeOptions()
        options.binary_location = chrome_path
        service = Service(executable_path=chromedriver_path)
        return webdriver.Chrome(service=service, options=options)

    @staticmethod
    def quit_driver(driver):
        if driver:
            driver.quit()
