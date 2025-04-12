import logging
from selenium.webdriver.common.by import By
import re
from robot.api import logger
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from libraries.common.log_manager import ColorLogger


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
            headers = [header.text.strip().lower() for header in rows[0].find_elements(By.XPATH, ".//th | .//td")]

            for row_index, expected_row in enumerate(expected_data, start=1):
                if row_index >= len(rows):
                    raise ValueError(f"Not enough rows in table. Expected at least {row_index}, but found {len(rows) - 1}")

                row = rows[row_index]
                cells = row.find_elements(By.XPATH, ".//td|.//th")

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
            headers = [header.text.strip().lower() for header in rows[0].find_elements(By.XPATH, ".//th | .//td")]

            if row_index < 1 or row_index >= len(rows):
                raise ValueError(f"Invalid row index: {row_index}. Table has {len(rows) - 1} data rows.")

            row = rows[row_index]
            cells = row.find_elements(By.XPATH, ".//td|.//th")

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
            headers = [header.text.strip().lower() for header in rows[0].find_elements(By.XPATH, ".//th | .//td")]

            if row_index < 1 or row_index >= len(rows):
                raise ValueError(f"Invalid row index: {row_index}. Table has {len(rows) - 1} data rows.")

            row = rows[row_index]
            cells = row.find_elements(By.XPATH, ".//td|.//th")

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
            result= actual_value == expected_value
            log_message = f"UI Verification: Asserting: {column}, exact_match, Expected: {expected_value}, Actual: {actual_value}"
            self._log_result(result, log_message)
            assert result, f"Mismatch in column '{column}'. Expected: {expected_value}, Actual: {actual_value}"
        elif match_type == 'partial':
            result = expected_value in actual_value
            log_message = f"UI Verification: Asserting: {column}, partial_match, Expected: {expected_value}, Actual: {actual_value}"
            self._log_result(result, log_message)
            assert result, f"Expected value '{expected_value}' not found in column '{column}'. Actual: {actual_value}"
        elif match_type == 'regex':
            result = re.search(expected_value, actual_value), f"Regex '{expected_value}' did not match in column '{column}'. Actual: {actual_value}"
            log_message = f"UI Verification: Asserting: {column}, regex_match, Expected: {expected_value}, Actual: {actual_value}"
            self._log_result(result, log_message)
            assert result, f"Regex '{expected_value}' did not match in column '{column}'. Actual: {actual_value}"
        else:
            raise ValueError(f"Invalid match_type: {match_type}")

        self.logger.debug(f"Verified column '{column}': {actual_value}")

    def verify_table_is_empty(self, table_element):
        """
        Verify that the table contains no data rows.

        :param table_element: WebElement of the table
        """
        try:
            rows = table_element.find_elements(By.TAG_NAME, "tr")
            assert len(rows) == 1, f"Table is not empty. Found {len(rows) - 1} data rows."

            self.logger.info("Table is empty as expected.")
        except Exception as e:
            self.logger.error(f"Error verifying if table is empty: {str(e)}")
            raise

    def verify_unique_column_values(self, table_element, column):
        """
        Verify that all values in a specific column are unique.

        :param table_element: WebElement of the table
        :param column: Column name or index to verify uniqueness
        """
        try:
            rows = table_element.find_elements(By.TAG_NAME, "tr")
            headers = [header.text.strip().lower() for header in rows[0].find_elements(By.XPATH, ".//th | .//td")]

            column_index = self._get_cell_index(headers, column)
            values = set()

            for row in rows[1:]:  # Skip header row
                cells = row.find_elements(By.XPATH, ".//td|.//th")
                if column_index < len(cells):
                    value = cells[column_index].text.strip()
                    assert value not in values, f"Duplicate value found in column '{column}': {value}"
                    values.add(value)

            self.logger.info(f"All values in column '{column}' are unique.")
        except Exception as e:
            self.logger.error(f"Error verifying unique values in column: {str(e)}")
            raise

    def verify_value_in_table(self, table_element, search_value):
        """
        Verify if a specific value exists in the table.

        :param table_element: WebElement of the table
        :param search_value: The value to search for in the table
        :return: True if the value is found, False if not
        """
        try:
            rows = table_element.find_elements(By.TAG_NAME, "tr")

            for row in rows[1:]:  # Skip header row
                cells = row.find_elements(By.XPATH, ".//td|.//th")
                for cell in cells:
                    if search_value in cell.text.strip():
                        self.logger.info(f"Value '{search_value}' found in table.")
                        return True

            self.logger.info(f"Value '{search_value}' not found in the table.")
            return False
        except Exception as e:
            self.logger.error(f"Error verifying presence of value in table: {str(e)}")
            raise

    def verify_value_not_in_table(self, table_element, search_value):
        """
        Verify if a specific value does not exist in the table.

        :param table_element: WebElement of the table
        :param search_value: The value to verify is not in the table
        :return: True if the value is not found, False if it is found
        """
        try:
            rows = table_element.find_elements(By.TAG_NAME, "tr")

            for row in rows[1:]:  # Skip header row
                cells = row.find_elements(By.XPATH, ".//td|.//th")
                for cell in cells:
                    if search_value in cell.text.strip():
                        self.logger.info(f"Value '{search_value}' found in table when it should not be present.")
                        return False

            self.logger.info(f"Value '{search_value}' not found in the table as expected.")
            return True
        except Exception as e:
            self.logger.error(f"Error verifying absence of value in table: {str(e)}")
            raise

    def verify_row_count(self, table_element, expected_row_count):
        """
        Verify the number of rows in the table (excluding the header row).

        :param table_element: WebElement of the table
        :param expected_row_count: The expected number of data rows
        """
        try:
            rows = table_element.find_elements(By.TAG_NAME, "tr")
            actual_row_count = len(rows) - 1  # Exclude header row

            assert actual_row_count == expected_row_count, \
                f"Row count mismatch. Expected: {expected_row_count}, Actual: {actual_row_count}"

            self.logger.info(f"Row count verified successfully: {actual_row_count}")
        except Exception as e:
            self.logger.error(f"Error verifying row count: {str(e)}")
            raise

    def verify_column_sorted(self, table_element, column, expected_order='ascending', strip_spaces=True):
        """
        Verify if a specific column in the table is sorted in the expected order.

        :param table_element: WebElement of the table
        :param column: Column name (or 1-based index) to verify sorting
        :param expected_order: Expected sorting order, either 'ascending' or 'descending' (default is 'ascending')
        :param strip_spaces: Boolean to determine whether to remove leading/trailing spaces from cell values (default is True)
        """
        try:
            # Retrieve all rows and headers of the table
            rows = table_element.find_elements(By.TAG_NAME, "tr")
            headers = [header.text.strip().lower() for header in rows[0].find_elements(By.XPATH, ".//th | .//td")]

            # Get the index of the target column
            column_index = self._get_cell_index(headers, column)

            # Collect all values from the target column (skipping the header row)
            column_data = []
            for row in rows[1:]:
                cells = row.find_elements(By.XPATH, ".//td|.//th")
                if column_index < len(cells):
                    cell_text = cells[column_index].text.strip()
                    if strip_spaces:
                        cell_text = cell_text.strip()  # Optionally strip spaces
                    column_data.append(cell_text)
                else:
                    raise ValueError(f"Column '{column}' is out of range. This row has {len(cells)} columns.")

            # Sort the column data based on the expected order
            sorted_data = sorted(column_data, key=lambda x: (x == '', x))
            if expected_order == 'descending':
                sorted_data.reverse()

            # Validate if the column data is sorted as expected
            assert column_data == sorted_data, f"Column '{column}' is not sorted in {expected_order} order."

            self.logger.info(f"Column '{column}' is correctly sorted in {expected_order} order.")
        except Exception as e:
            self.logger.error(f"Error verifying sorting for column '{column}': {str(e)}")
            raise

    def verify_numeric_column_sorted(self, table_element, column, expected_order='ascending', strip_spaces=True):

        try:
            # Retrieve all rows and headers of the table
            rows = table_element.find_elements(By.TAG_NAME, "tr")
            headers = [header.text.strip().lower() for header in rows[0].find_elements(By.XPATH, ".//th | .//td")]

            # Get the index of the target column using the existing helper method
            column_index = self._get_cell_index(headers, column)

            # Collect numeric values from the target column (skipping the header row)
            numeric_data = []
            for row in rows[1:]:
                cells = row.find_elements(By.XPATH, ".//td|.//th")
                if column_index < len(cells):
                    cell_text = cells[column_index].text
                    if strip_spaces:
                        cell_text = cell_text.strip()
                    # Remove commas if present
                    cell_text_no_comma = cell_text.replace(",", "")
                    try:
                        # Convert the processed string to a float
                        numeric_value = float(cell_text_no_comma)
                    except ValueError:
                        raise ValueError(f"Cell value '{cell_text}' in column '{column}' is not a valid number.")
                    numeric_data.append(numeric_value)
                else:
                    raise ValueError(f"Column '{column}' is out of range. This row has {len(cells)} columns.")

            # Sort the numeric data based on the expected order
            sorted_data = sorted(numeric_data)
            if expected_order == 'descending':
                sorted_data.reverse()

            # Validate if the column data is sorted as expected
            assert numeric_data == sorted_data, f"Column '{column}' is not sorted in {expected_order} order. Actual order: {numeric_data}"

            self.logger.info(f"Numeric column '{column}' is correctly sorted in {expected_order} order.")
        except Exception as e:
            self.logger.error(f"Error verifying numeric sorting for column '{column}': {str(e)}")
            raise

    def select_table_row_checkbox(self, table_element, identifier_column, identifier_value, checkbox_column=1):
        """
        Select the checkbox in a specific row based on an identifier value in a specific column.

        :param table_element: WebElement of the table
        :param identifier_column: Column name or index (1-based if index) containing the identifier
        :param identifier_value: Value to identify the row
        :param checkbox_column: Column index (1-based) of the checkbox (default is 1, assuming checkbox is in the first column)
        """
        try:
            rows = table_element.find_elements(By.TAG_NAME, "tr")
            headers = [header.text.strip().lower() for header in rows[0].find_elements(By.XPATH, ".//th | .//td")]

            identifier_index = self._get_cell_index(headers, identifier_column)
            checkbox_index = checkbox_column - 1  # Convert to 0-based index

            for row in rows[1:]:  # Skip header row
                cells = row.find_elements(By.XPATH, ".//td|.//th")
                if identifier_index < len(cells) and cells[identifier_index].text.strip() == identifier_value:
                    if checkbox_index < len(cells):
                        checkbox = cells[checkbox_index].find_element(By.TAG_NAME, "input")
                        if checkbox.get_attribute("type") == "checkbox":
                            if not checkbox.is_selected():
                                checkbox.click()
                            self.logger.info(f"Checkbox selected for row with {identifier_column}: {identifier_value}")
                            return
                    else:
                        raise ValueError(
                            f"Checkbox column index {checkbox_column} is out of range. Row has {len(cells)} cells.")

            raise ValueError(f"No row found with {identifier_column}: {identifier_value}")

        except Exception as e:
            self.logger.error(f"Error selecting row checkbox: {str(e)}")
            raise

    def select_multiple_table_row_checkboxes(self, table_element, identifier_column, identifier_values, checkbox_column=1):
        """
        Select checkboxes in multiple rows based on identifier values in a specific column.

        :param table_element: WebElement of the table
        :param identifier_column: Column name or index (1-based if index) containing the identifier
        :param identifier_values: List of values to identify the rows
        :param checkbox_column: Column index (1-based) of the checkbox (default is 1, assuming checkbox is in the first column)
        """
        for identifier_value in identifier_values:
            self.select_table_row_checkbox(table_element, identifier_column, identifier_value, checkbox_column)

    def _log_result(self, success: bool, message: str):
        """Logs the result of a check with appropriate color."""
        logging.debug(f"{self.__class__.__name__}: {message}")
        logger.info(
            ColorLogger.success(f"=> {message}") if success else ColorLogger.error(f"=> {message}"), html=True)

    def click_table_header_column(self, table_element, column):
        """
        Click on a specific column header in the table.

        :param table_element: WebElement of the table
        :param column: Column name or index (1-based if index) to click
        :return: None
        """
        try:
            # Get the first row (header row)
            header_row = table_element.find_element(By.TAG_NAME, "tr")
            headers = [header.text.strip().lower() for header in header_row.find_elements(By.XPATH, ".//th | .//td")]

            # Use existing _get_cell_index method to find the column index
            column_index = self._get_cell_index(headers, column)

            # Get all header elements and click the one at the determined index
            header_elements = header_row.find_elements(By.XPATH, ".//th | .//td")
            if column_index >= len(header_elements):
                raise ValueError(f"Column index {column_index} is out of range. Found {len(header_elements)} header columns.")

            header_element = header_elements[column_index]
            WebDriverWait(self.driver, 60).until(EC.element_to_be_clickable(header_element))
            self.driver.execute_script("arguments[0].scrollIntoView();", header_element)
            header_element.click()
            self.logger.info(f"Clicked on table header column: '{column}'")

        except Exception as e:
            self.logger.error(f"Error clicking table header column: {str(e)}")
            raise