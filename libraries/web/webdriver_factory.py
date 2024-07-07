import os
import yaml
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.edge.options import Options as EdgeOptions
from libraries.common.log_manager import logger


class WebDriverFactory:
    @staticmethod
    def create_driver(config_path):
        logger.info(f"Creating WebDriver using config file: {config_path}")

        with open(config_path, 'r') as file:
            config = yaml.safe_load(file)
        logger.debug(f"Loaded configuration: {config}")

        browser = config['browser']
        is_remote = config.get('is_remote', False)
        remote_url = config.get('remote_url')
        browser_options = config.get('browser_options', {})

        logger.info(f"Configuring for browser: {browser}")
        logger.info(f"Remote execution: {'Yes' if is_remote else 'No'}")

        if browser.lower() == 'chrome':
            options = ChromeOptions()
            service = ChromeService(executable_path=config.get('chromedriver_path'))
            browser_path = config.get('chrome_path')
            logger.info(f"Using ChromeDriver path: {config.get('chromedriver_path')}")
        elif browser.lower() == 'edge':
            options = EdgeOptions()
            service = EdgeService(executable_path=config.get('edgedriver_path'))
            browser_path = config.get('edge_path')
            logger.info(f"Using EdgeDriver path: {config.get('edgedriver_path')}")
        else:
            logger.error(f"Unsupported browser: {browser}")
            raise ValueError(f"Unsupported browser: {browser}")

        # 设置浏览器路径
        if browser_path:
            options.binary_location = browser_path
            logger.info(f"Set browser binary location: {browser_path}")

        # 设置浏览器选项
        logger.info("Configuring browser options:")
        for option, value in browser_options.items():
            if isinstance(value, bool) and value:
                options.add_argument(f'--{option}')
                logger.debug(f"Added browser option: --{option}")
            elif isinstance(value, str):
                options.add_argument(f'--{option}={value}')
                logger.debug(f"Added browser option: --{option}={value}")

        if is_remote:
            if not remote_url:
                logger.error("Remote URL is required for remote execution")
                raise ValueError("Remote URL is required for remote execution")
            logger.info(f"Creating remote WebDriver with URL: {remote_url}")
            driver = webdriver.Remote(command_executor=remote_url, options=options)
        else:
            if browser.lower() == 'chrome':
                logger.info("Creating local Chrome WebDriver")
                driver = webdriver.Chrome(service=service, options=options)
            elif browser.lower() == 'edge':
                logger.info("Creating local Edge WebDriver")
                driver = webdriver.Edge(service=service, options=options)

        logger.info("WebDriver created successfully")
        return driver

    @staticmethod
    def quit_driver(driver):
        if driver:
            logger.info("Quitting WebDriver")
            driver.quit()
            logger.info("WebDriver quit successfully")
        else:
            logger.warning("Attempted to quit a non-existent WebDriver")