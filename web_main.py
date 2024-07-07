import os
from libraries.common.config_manager import ConfigManager
from libraries.web.e2e_test_executor import E2ETestExecutor
from libraries.web.excel_reader import ExcelReader
from libraries.web.webdriver_factory import WebDriverFactory
from libraries.common.utility_helpers import PROJECT_ROOT

def main():
    project_root: str = PROJECT_ROOT
    config_path = os.path.join(project_root,  'configs', 'web', 'web_config.yaml')
    test_config = ConfigManager.load_yaml(config_path)

    test_case_path = test_config.get("test_case_path", None)

    excel_data_manager = ExcelReader(test_case_path)
    driver = WebDriverFactory.create_driver(config_path)

    try:
        test_executor = E2ETestExecutor(driver, excel_data_manager)
        test_executor.run_tests()
    finally:
        WebDriverFactory.quit_driver(driver)


if __name__ == "__main__":
    main()