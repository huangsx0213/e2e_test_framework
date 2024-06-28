from e2e_test_executor import E2ETestExecutor
from libraries.web.excel_reader import ExcelReader
from libraries.web.webdriver_factory import WebDriverFactory


def main():
    excel_path = 'test_cases/e2e_test_cases.xlsx'
    chrome_path = r"E:\Downloads\my files\chrome-win64\chrome.exe"
    chromedriver_path = r"E:\Downloads\my files\chromedriver-win64\chromedriver.exe"

    excel_data_manager = ExcelReader(excel_path)
    driver = WebDriverFactory.create_chrome_driver(chrome_path, chromedriver_path)

    try:
        test_executor = E2ETestExecutor(driver, excel_data_manager)
        test_executor.run_tests()
    finally:
        WebDriverFactory.quit_driver(driver)


if __name__ == "__main__":
    main()
