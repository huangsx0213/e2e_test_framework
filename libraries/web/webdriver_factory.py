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

        logging.info(f"{WebDriverFactory.__class__.__name__}: Configuring for browser: {browser}")
        logging.info(f"{WebDriverFactory.__class__.__name__}: Remote execution: {'Yes' if is_remote else 'No'}")

        if browser.lower() == 'chrome':
            options = ChromeOptions()
            service = ChromeService(executable_path=driver_config.get('chromedriver_path'))
            browser_path = driver_config.get('chrome_path')
            logging.info(f"{WebDriverFactory.__class__.__name__}: Using ChromeDriver path: {driver_config.get('chromedriver_path')}")
        elif browser.lower() == 'edge':
            options = EdgeOptions()
            service = EdgeService(executable_path=driver_config.get('edgedriver_path'))
            browser_path = driver_config.get('edge_path')
            logging.info(f"{WebDriverFactory.__class__.__name__}: Using EdgeDriver path: {driver_config.get('edgedriver_path')}")
        else:
            logging.error(f"{WebDriverFactory.__class__.__name__}: Unsupported browser: {browser}")
            raise ValueError(f"{WebDriverFactory.__class__.__name__}: Unsupported browser: {browser}")

        # 设置浏览器路径
        if browser_path and not is_remote:
            options.binary_location = browser_path
            logging.info(f"{WebDriverFactory.__class__.__name__}: Set browser binary location: {browser_path}")

        # 设置浏览器选项
        logging.info("Configuring browser options:")
        for option, value in browser_options.items():
            if isinstance(value, bool) and value:
                options.add_argument(f'--{option}')
                logging.info(f"{WebDriverFactory.__class__.__name__}: Added browser option: --{option}")
            elif isinstance(value, str):
                options.add_argument(f'--{option}={value}')
                logging.info(f"{WebDriverFactory.__class__.__name__}: Added browser option: --{option}={value}")

        if is_remote:
            if not remote_url:
                logging.error(f"{WebDriverFactory.__class__.__name__}: Remote URL is required for remote execution")
                raise ValueError(f"{WebDriverFactory.__class__.__name__}: Remote URL is required for remote execution")
            logging.info(f"{WebDriverFactory.__class__.__name__}: Creating remote WebDriver with URL: {remote_url}")
            driver = webdriver.Remote(command_executor=remote_url, options=options)
        else:
            if browser.lower() == 'chrome':
                logging.info(f"{WebDriverFactory.__class__.__name__}: Creating local Chrome WebDriver")
                driver = webdriver.Chrome(service=service, options=options)
            elif browser.lower() == 'edge':
                logging.info(f"{WebDriverFactory.__class__.__name__}: Creating local Edge WebDriver")
                driver = webdriver.Edge(service=service, options=options)

        logging.info(f"{WebDriverFactory.__class__.__name__}: WebDriver created successfully")
        return driver

    @staticmethod
    def quit_driver(driver):
        if driver:
            logging.info(f"{WebDriverFactory.__class__.__name__}: Quitting WebDriver")
            driver.quit()
            logging.info(f"{WebDriverFactory.__class__.__name__}: WebDriver quit successfully")
        else:
            logging.warning(f"{WebDriverFactory.__class__.__name__}: Attempted to quit a non-existent WebDriver")
