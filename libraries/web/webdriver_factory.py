import os
import yaml
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.edge.options import Options as EdgeOptions

class WebDriverFactory:
    @staticmethod
    def create_driver(config_path):
        with open(config_path, 'r') as file:
            config = yaml.safe_load(file)

        browser = config['browser']
        is_remote = config.get('is_remote', False)
        remote_url = config.get('remote_url')
        browser_options = config.get('browser_options', {})

        if browser.lower() == 'chrome':
            options = ChromeOptions()
            service = ChromeService(executable_path=config.get('chromedriver_path'))
            browser_path = config.get('chrome_path')
        elif browser.lower() == 'edge':
            options = EdgeOptions()
            service = EdgeService(executable_path=config.get('edgedriver_path'))
            browser_path = config.get('edge_path')
        else:
            raise ValueError(f"Unsupported browser: {browser}")

        # 设置浏览器路径
        if browser_path:
            options.binary_location = browser_path

        # 设置浏览器选项
        for option, value in browser_options.items():
            if isinstance(value, bool) and value:
                options.add_argument(f'--{option}')
            elif isinstance(value, str):
                options.add_argument(f'--{option}={value}')

        if is_remote:
            if not remote_url:
                raise ValueError("Remote URL is required for remote execution")
            return webdriver.Remote(command_executor=remote_url, options=options)
        else:
            if browser.lower() == 'chrome':
                return webdriver.Chrome(service=service, options=options)
            elif browser.lower() == 'edge':
                return webdriver.Edge(service=service, options=options)

    @staticmethod
    def quit_driver(driver):
        if driver:
            driver.quit()