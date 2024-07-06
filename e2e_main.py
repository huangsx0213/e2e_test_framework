import os

from libraries.common.config_manager import ConfigManager
from libraries.e2e.e2e_test_executor import E2ETestExecutor
from libraries.web.excel_reader import ExcelReader
from libraries.web.webdriver_factory import WebDriverFactory
from libraries.common.utility_helpers import UtilityHelpers, PROJECT_ROOT

def main():
    project_root: str = PROJECT_ROOT
    config_path = os.path.join(project_root,  'configs', 'e2e', 'e2e_config.yaml')
    test_config = ConfigManager.load_yaml(config_path)

    chrome_path = test_config.get("chrome_path", None)
    chromedriver_path = test_config.get("chromedriver_path", None)
    test_case_path = test_config.get("test_case_path", None)

    excel_data_manager = ExcelReader(test_case_path)
    driver = WebDriverFactory.create_chrome_driver(chrome_path, chromedriver_path)

    try:
        test_executor = E2ETestExecutor(driver, excel_data_manager)
        test_executor.run_tests()
    finally:
        WebDriverFactory.quit_driver(driver)


if __name__ == "__main__":
    main()