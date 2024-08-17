import logging
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.edge.options import Options as EdgeOptions


class WebDriverFactory:
    @staticmethod
    def create_driver(driver_config):
        browser = driver_config['browser']
        is_remote = driver_config.get('is_remote', False)
        remote_url = driver_config.get('remote_url')
        browser_options = driver_config.get('browser_options', {})

        logging.info(f"WebDriverFactory: Configuring for browser: {browser}")
        logging.info(f"WebDriverFactory: Remote execution: {'Yes' if is_remote else 'No'}")
        browser_path = None
        if browser.lower() == 'chrome':
            options = ChromeOptions()
            if not is_remote:
                service = ChromeService(executable_path=driver_config.get('chrome_driver_path'))
                browser_path = driver_config.get('chrome_path')
                logging.info(f"WebDriverFactory: Using ChromeDriver path: {driver_config.get('chrome_driver_path')}")
        elif browser.lower() == 'edge':
            options = EdgeOptions()
            if not is_remote:
                service = EdgeService(executable_path=driver_config.get('edge_driver_path'))
                browser_path = driver_config.get('edge_path')
                logging.info(f"WebDriverFactory: Using EdgeDriver path: {driver_config.get('edge_driver_path')}")
        else:
            logging.error(f"WebDriverFactory: Unsupported browser: {browser}")
            raise ValueError(f"WebDriverFactory: Unsupported browser: {browser}")

        # 设置浏览器路径
        if browser_path and not is_remote:
            options.binary_location = browser_path
            logging.info(f"WebDriverFactory: Set browser binary location: {browser_path}")

        # 设置浏览器选项
        logging.info("WebDriverFactory: Configuring browser options:")
        for option, value in browser_options.items():
            if isinstance(value, bool) and value:
                options.add_argument(f'--{option}')
                logging.info(f"WebDriverFactory: Added browser option: --{option}")
            elif isinstance(value, str):
                options.add_argument(f'--{option}={value}')
                logging.info(f"WebDriverFactory: Added browser option: --{option}={value}")

        if is_remote:
            if not remote_url:
                logging.error(f"WebDriverFactory: Remote URL is required for remote execution")
                raise ValueError(f"WebDriverFactory: Remote URL is required for remote execution")
            logging.info(f"WebDriverFactory: Creating remote WebDriver with URL: {remote_url}")
            driver = webdriver.Remote(command_executor=remote_url, options=options)
        else:
            if browser.lower() == 'chrome':
                logging.info(f"WebDriverFactory: Creating local Chrome WebDriver")
                driver = webdriver.Chrome(service=service, options=options)
            elif browser.lower() == 'edge':
                logging.info(f"WebDriverFactory: Creating local Edge WebDriver")
                driver = webdriver.Edge(service=service, options=options)

        logging.info(f"WebDriverFactory: WebDriver created successfully")
        return driver

    @staticmethod
    def quit_driver(driver):
        if driver:
            logging.info(f"WebDriverFactory: Quitting WebDriver")
            driver.close()
            logging.info(f"WebDriverFactory: WebDriver quit successfully")
        else:
            logging.warning(f"WebDriverFactory: Attempted to quit a non-existent WebDriver")
