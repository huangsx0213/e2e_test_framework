import logging
from selenium.webdriver.common.by import By

import re


class TableVerifier:
    def __init__(self, driver):
        self.driver = driver
        self.logger = logging.getLogger(__name__)

    def verify_table(self, table_element, expected_data, match_type='exact'):
        """
        Verify the entire table data.

        :param table_element: WebElement of the table
        :param expected_data: List of dictionaries, each representing a row
        :param match_type: Type of matching to perform ('exact', 'partial', 'regex')
        """
        try:
            rows = table_element.find_elements(By.TAG_NAME, "tr")
            headers = [header.text.strip().lower() for header in rows[0].find_elements(By.TAG_NAME, "th")]

            for row_index, expected_row in enumerate(expected_data, start=1):
                if row_index >= len(rows):
                    raise ValueError(f"Not enough rows in table. Expected at least {row_index}, but found {len(rows) - 1}")

                row = rows[row_index]
                cells = row.find_elements(By.TAG_NAME, "td")

                for column, expected_value in expected_row.items():
                    cell_index = self._get_cell_index(headers, column)
                    if cell_index >= len(cells):
                        raise ValueError(f"Column '{column}' is out of range. Row has {len(cells)} cells.")

                    actual_value = cells[cell_index].text.strip()
                    self._verify_cell_value(column, actual_value, expected_value, match_type)

            self.logger.info("All table data verified successfully.")
        except Exception as e:
            self.logger.error(f"Error verifying table data: {str(e)}")
            raise

    def verify_table_row(self, table_element, row_index, expected_data, match_type='exact'):
        """
        Verify the data in a specific row of a table.

        :param table_element: WebElement of the table
        :param row_index: Index of the row to verify (1-based index)
        :param expected_data: Dictionary of column name (or index) and expected value
        :param match_type: Type of matching to perform ('exact', 'partial', 'regex')
        """
        try:
            rows = table_element.find_elements(By.TAG_NAME, "tr")
            headers = [header.text.strip().lower() for header in rows[0].find_elements(By.TAG_NAME, "th")]

            if row_index < 1 or row_index >= len(rows):
                raise ValueError(f"Invalid row index: {row_index}. Table has {len(rows) - 1} data rows.")

            row = rows[row_index]
            cells = row.find_elements(By.TAG_NAME, "td")

            for column, expected_value in expected_data.items():
                cell_index = self._get_cell_index(headers, column)
                if cell_index >= len(cells):
                    raise ValueError(f"Column '{column}' is out of range. Row has {len(cells)} cells.")

                actual_value = cells[cell_index].text.strip()
                self._verify_cell_value(column, actual_value, expected_value, match_type)

            self.logger.info(f"All expected data in row {row_index} verified successfully.")
        except Exception as e:
            self.logger.error(f"Error verifying table row data: {str(e)}")
            raise

    def verify_specific_cell(self, table_element, row_index, column, expected_value, match_type='exact'):
        """
        Verify the data in a specific cell of a table.

        :param table_element: WebElement of the table
        :param row_index: Index of the row to verify (1-based index)
        :param column: Column name or index (1-based if index)
        :param expected_value: Expected value of the cell
        :param match_type: Type of matching to perform ('exact', 'partial', 'regex')
        """
        try:
            rows = table_element.find_elements(By.TAG_NAME, "tr")
            headers = [header.text.strip().lower() for header in rows[0].find_elements(By.TAG_NAME, "th")]

            if row_index < 1 or row_index >= len(rows):
                raise ValueError(f"Invalid row index: {row_index}. Table has {len(rows) - 1} data rows.")

            row = rows[row_index]
            cells = row.find_elements(By.TAG_NAME, "td")

            cell_index = self._get_cell_index(headers, column)
            if cell_index >= len(cells):
                raise ValueError(f"Column '{column}' is out of range. Row has {len(cells)} cells.")

            actual_value = cells[cell_index].text.strip()
            self._verify_cell_value(column, actual_value, expected_value, match_type)

            self.logger.info(f"Cell at row {row_index}, column '{column}' verified successfully.")
        except Exception as e:
            self.logger.error(f"Error verifying specific cell: {str(e)}")
            raise

    def _get_cell_index(self, headers, column):
        """
        Get the index of a cell based on column name or index.
        """
        if isinstance(column, int):
            return column - 1  # Convert to 0-based index

        column_lower = column.lower()
        for i, header in enumerate(headers):
            if header == column_lower:
                return i

        raise ValueError(f"Column '{column}' not found in table headers.")

    def _verify_cell_value(self, column, actual_value, expected_value, match_type):
        """
        Verify cell value based on the specified match type.
        """
        if match_type == 'exact':
            assert actual_value == expected_value, f"Mismatch in column '{column}'. Expected: {expected_value}, Actual: {actual_value}"
            logging.info(f"Verified column '{column}': expected: {expected_value}, actual: {actual_value}")
        elif match_type == 'partial':
            assert expected_value in actual_value, f"Value '{expected_value}' not found in column '{column}'. Actual: {actual_value}"
            logging.info(f"Verified column '{column}': partial match: {expected_value} in {actual_value}")
        elif match_type == 'regex':
            assert re.search(expected_value, actual_value), f"Regex '{expected_value}' did not match in column '{column}'. Actual: {actual_value}"
            logging.info(f"Verified column '{column}': regex match: {expected_value} in {actual_value}")
        else:
            raise ValueError(f"Invalid match_type: {match_type}")

        self.logger.info(f"Verified column '{column}': {actual_value}")

# 使用示例
# table_verifier = TableVerifier(driver)
# table_element = driver.find_element(By.ID, 'myTable')

# 验证整个表格
# table_verifier.verify_table(
#     table_element,
#     expected_data=[
#         {'Name': 'John Doe', 'Age': '30', 'Email': r'^[\w\.-]+@[\w\.-]+\.\w+$'},
#         {'Name': 'Jane Smith', 'Age': '25', 'Email': r'^[\w\.-]+@[\w\.-]+\.\w+$'}
#     ],
#     match_type='regex'
# )

# 验证特定行
# table_verifier.verify_table_row(
#     table_element,
#     row_index=2,
#     expected_data={
#         'Name': 'Jane Smith',
#         'Age': '25',
#         'Email': r'^[\w\.-]+@[\w\.-]+\.\w+$'
#     },
#     match_type='regex'
# )

# 验证特定单元格
# table_verifier.verify_specific_cell(
#     table_element,
#     row_index=2,
#     column='Email',
#     expected_value=r'^[\w\.-]+@[\w\.-]+\.\w+$',
#     match_type='regex'
# )