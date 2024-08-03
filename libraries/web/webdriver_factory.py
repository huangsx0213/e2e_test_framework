import logging
import yaml
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.edge.options import Options as EdgeOptions


class WebDriverFactory:
    @staticmethod
    def create_driver(config_path):
        logging.info(f"Creating WebDriver using config file: {config_path}")

        with open(config_path, 'r') as file:
            config = yaml.safe_load(file)
        logging.debug(f"Loaded configuration: {config}")

        browser = config['browser']
        is_remote = config.get('is_remote', False)
        remote_url = config.get('remote_url')
        browser_options = config.get('browser_options', {})

        logging.info(f"Configuring for browser: {browser}")
        logging.info(f"Remote execution: {'Yes' if is_remote else 'No'}")

        if browser.lower() == 'chrome':
            options = ChromeOptions()
            service = ChromeService(executable_path=config.get('chromedriver_path'))
            browser_path = config.get('chrome_path')
            logging.info(f"Using ChromeDriver path: {config.get('chromedriver_path')}")
        elif browser.lower() == 'edge':
            options = EdgeOptions()
            service = EdgeService(executable_path=config.get('edgedriver_path'))
            browser_path = config.get('edge_path')
            logging.info(f"Using EdgeDriver path: {config.get('edgedriver_path')}")
        else:
            logging.error(f"Unsupported browser: {browser}")
            raise ValueError(f"Unsupported browser: {browser}")

        # 设置浏览器路径
        if browser_path and not is_remote:
            options.binary_location = browser_path
            logging.info(f"Set browser binary location: {browser_path}")

        # 设置浏览器选项
        logging.info("Configuring browser options:")
        for option, value in browser_options.items():
            if isinstance(value, bool) and value:
                options.add_argument(f'--{option}')
                logging.info(f"Added browser option: --{option}")
            elif isinstance(value, str):
                options.add_argument(f'--{option}={value}')
                logging.info(f"Added browser option: --{option}={value}")

        if is_remote:
            if not remote_url:
                logging.error("Remote URL is required for remote execution")
                raise ValueError("Remote URL is required for remote execution")
            logging.info(f"Creating remote WebDriver with URL: {remote_url}")
            driver = webdriver.Remote(command_executor=remote_url, options=options)
        else:
            if browser.lower() == 'chrome':
                logging.info("Creating local Chrome WebDriver")
                driver = webdriver.Chrome(service=service, options=options)
            elif browser.lower() == 'edge':
                logging.info("Creating local Edge WebDriver")
                driver = webdriver.Edge(service=service, options=options)

        logging.info("WebDriver created successfully")
        return driver

    @staticmethod
    def quit_driver(driver):
        if driver:
            logging.info("Quitting WebDriver")
            driver.quit()
            logging.info("WebDriver quit successfully")
        else:
            logging.warning("Attempted to quit a non-existent WebDriver")