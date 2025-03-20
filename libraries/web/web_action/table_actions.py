from .base import Base
from typing import Union, List, Dict
from selenium.webdriver.remote.webelement import WebElement
import logging

class TableActions(Base):
    def verify_table_exact(self, locator: Union[tuple, WebElement], expected_data: List[Dict[str, str]], element_desc=None):
        logging.debug(f"{self.__class__.__name__}: Verifying entire table with exact match")
        table_element = self.wait_for_element(locator, element_desc=element_desc) if isinstance(locator, tuple) else locator
        table_desc = element_desc or self._get_element_description(table_element)
        self.table_verifier.verify_table(table_element, expected_data, match_type='exact')
        logging.debug(f"{self.__class__.__name__}: Table verification (exact match) completed for table: {table_desc}")

    def verify_table_row_exact(self, locator: Union[tuple, WebElement], row_index: int, expected_data: Dict[str, str], element_desc=None):
        logging.debug(f"{self.__class__.__name__}: Verifying table row at index {row_index} with exact match")
        table_element = self.wait_for_element(locator, element_desc=element_desc) if isinstance(locator, tuple) else locator
        table_desc = element_desc or self._get_element_description(table_element)
        self.table_verifier.verify_table_row(table_element, row_index, expected_data, match_type='exact')
        logging.debug(f"{self.__class__.__name__}: Table row verification (exact match) completed for table: {table_desc}, row: {row_index}")

    def verify_specific_cell_exact(self, locator: Union[tuple, WebElement], row_index: int, column: Union[str, int], expected_value: str, element_desc=None):
        logging.debug(f"{self.__class__.__name__}: Verifying specific cell at row {row_index}, column {column} with exact match")
        table_element = self.wait_for_element(locator, element_desc=element_desc) if isinstance(locator, tuple) else locator
        table_desc = element_desc or self._get_element_description(table_element)
        self.table_verifier.verify_specific_cell(table_element, row_index, column, expected_value, match_type='exact')
        logging.debug(f"{self.__class__.__name__}: Specific cell verification (exact match) completed for table: {table_desc}, row: {row_index}, column: {column}")

    def verify_table_partial(self, locator: Union[tuple, WebElement], expected_data: List[Dict[str, str]], element_desc=None):
        logging.debug(f"{self.__class__.__name__}: Verifying entire table with partial match")
        table_element = self.wait_for_element(locator, element_desc=element_desc) if isinstance(locator, tuple) else locator
        table_desc = element_desc or self._get_element_description(table_element)
        self.table_verifier.verify_table(table_element, expected_data, match_type='partial')
        logging.debug(f"{self.__class__.__name__}: Table verification (partial match) completed for table: {table_desc}")

    def verify_table_row_partial(self, locator: Union[tuple, WebElement], row_index: int, expected_data: Dict[str, str], element_desc=None):
        logging.debug(f"{self.__class__.__name__}: Verifying table row at index {row_index} with partial match")
        table_element = self.wait_for_element(locator, element_desc=element_desc) if isinstance(locator, tuple) else locator
        table_desc = element_desc or self._get_element_description(table_element)
        self.table_verifier.verify_table_row(table_element, row_index, expected_data, match_type='partial')
        logging.debug(f"{self.__class__.__name__}: Table row verification (partial match) completed for table: {table_desc}, row: {row_index}")

    def verify_specific_cell_partial(self, locator: Union[tuple, WebElement], row_index: int, column: Union[str, int], expected_value: str, element_desc=None):
        logging.debug(f"{self.__class__.__name__}: Verifying specific cell at row {row_index}, column {column} with partial match")
        table_element = self.wait_for_element(locator, element_desc=element_desc) if isinstance(locator, tuple) else locator
        table_desc = element_desc or self._get_element_description(table_element)
        self.table_verifier.verify_specific_cell(table_element, row_index, column, expected_value, match_type='partial')
        logging.debug(f"{self.__class__.__name__}: Specific cell verification (partial match) completed for table: {table_desc}, row: {row_index}, column: {column}")

    def verify_table_regex(self, locator: Union[tuple, WebElement], expected_data: List[Dict[str, str]], element_desc=None):
        logging.debug(f"{self.__class__.__name__}: Verifying entire table with regex match")
        table_element = self.wait_for_element(locator, element_desc=element_desc) if isinstance(locator, tuple) else locator
        table_desc = element_desc or self._get_element_description(table_element)
        self.table_verifier.verify_table(table_element, expected_data, match_type='regex')
        logging.debug(f"{self.__class__.__name__}: Table verification (regex match) completed for table: {table_desc}")

    def verify_table_row_regex(self, locator: Union[tuple, WebElement], row_index: int, expected_data: Dict[str, str], element_desc=None):
        logging.debug(f"{self.__class__.__name__}: Verifying table row at index {row_index} with regex match")
        table_element = self.wait_for_element(locator, element_desc=element_desc) if isinstance(locator, tuple) else locator
        table_desc = element_desc or self._get_element_description(table_element)
        self.table_verifier.verify_table_row(table_element, row_index, expected_data, match_type='regex')
        logging.debug(f"{self.__class__.__name__}: Table row verification (regex match) completed for table: {table_desc}, row: {row_index}")

    def verify_specific_cell_regex(self, locator: Union[tuple, WebElement], row_index: int, column: Union[str, int], expected_value: str, element_desc=None):
        logging.debug(f"{self.__class__.__name__}: Verifying specific cell at row {row_index}, column {column} with regex match")
        table_element = self.wait_for_element(locator, element_desc=element_desc) if isinstance(locator, tuple) else locator
        table_desc = element_desc or self._get_element_description(table_element)
        self.table_verifier.verify_specific_cell(table_element, row_index, column, expected_value, match_type='regex')
        logging.debug(f"{self.__class__.__name__}: Specific cell verification (regex match) completed for table: {table_desc}, row: {row_index}, column: {column}")

    def verify_table_is_empty(self, locator: Union[tuple, WebElement], element_desc=None):
        logging.debug(f"{self.__class__.__name__}: Verifying table is empty")
        try:
            table_element = self.wait_for_element(locator, element_desc=element_desc) if isinstance(locator, tuple) else locator
            table_desc = element_desc or self._get_element_description(table_element)
            self.table_verifier.verify_table_is_empty(table_element)
            logging.debug(f"{self.__class__.__name__}: Table empty verification completed successfully for table: {table_desc}")
        except Exception as e:
            logging.error(f"{self.__class__.__name__}: Error verifying table is empty: {str(e)}")
            raise

    def verify_unique_column_values(self, locator: Union[tuple, WebElement], column: Union[str, int], element_desc=None):
        logging.debug(f"{self.__class__.__name__}: Verifying unique values in column: {column}")
        try:
            table_element = self.wait_for_element(locator, element_desc=element_desc) if isinstance(locator, tuple) else locator
            table_desc = element_desc or self._get_element_description(table_element)
            self.table_verifier.verify_unique_column_values(table_element, column)
            logging.debug(f"{self.__class__.__name__}: Unique column values verification completed successfully for table: {table_desc}, column: {column}")
        except Exception as e:
            logging.error(f"{self.__class__.__name__}: Error verifying unique column values: {str(e)}")
            raise

    def verify_value_in_table(self, locator: Union[tuple, WebElement], search_value: str, element_desc=None):
        logging.debug(f"{self.__class__.__name__}: Verifying value '{search_value}' exists in table")
        try:
            table_element = self.wait_for_element(locator, element_desc=element_desc) if isinstance(locator, tuple) else locator
            table_desc = element_desc or self._get_element_description(table_element)
            result = self.table_verifier.verify_value_in_table(table_element, search_value)
            assert result,f"Value '{search_value}' not found in table"
            logging.debug(f"{self.__class__.__name__}: Value verification in table completed successfully for table: {table_desc}")
            return result
        except Exception as e:
            logging.error(f"{self.__class__.__name__}: Error verifying value in table: {str(e)}")
            raise

    def verify_value_not_in_table(self, locator: Union[tuple, WebElement], search_value: str, element_desc=None):
        logging.debug(f"{self.__class__.__name__}: Verifying value '{search_value}' does not exist in table")
        try:
            table_element = self.wait_for_element(locator, element_desc=element_desc) if isinstance(locator, tuple) else locator
            table_desc = element_desc or self._get_element_description(table_element)
            result = self.table_verifier.verify_value_not_in_table(table_element, search_value)
            assert result,f"Value '{search_value}' found in table when it should not be present"
            logging.debug(f"{self.__class__.__name__}: Value absence verification in table completed successfully for table: {table_desc}")
            return result
        except Exception as e:
            logging.error(f"{self.__class__.__name__}: Error verifying value not in table: {str(e)}")
            raise

    def click_table_header_column(self, locator: Union[tuple, WebElement], column: Union[str, int], element_desc=None):
        logging.debug(f"{self.__class__.__name__}: Clicking header column '{column}' in table")
        try:
            table_element = self.wait_for_element(locator, element_desc=element_desc) if isinstance(locator, tuple) else locator
            table_desc = element_desc or self._get_element_description(table_element)
            self.table_verifier.click_table_header_column(table_element, column)
            logging.debug(f"{self.__class__.__name__}: Clicked header column '{column}' successfully in table: {table_desc}")
        except Exception as e:
            logging.error(f"{self.__class__.__name__}: Error clicking table header column: {str(e)}")
            raise
    def verify_row_count(self, locator: Union[tuple, WebElement], expected_row_count: int, element_desc=None):
        logging.debug(f"{self.__class__.__name__}: Verifying row count: expected {expected_row_count}")
        try:
            table_element = self.wait_for_element(locator, element_desc=element_desc) if isinstance(locator, tuple) else locator
            table_desc = element_desc or self._get_element_description(table_element)
            self.table_verifier.verify_row_count(table_element, expected_row_count)
            logging.debug(f"{self.__class__.__name__}: Row count verification completed successfully for table: {table_desc}")
        except Exception as e:
            logging.error(f"{self.__class__.__name__}: Error verifying row count: {str(e)}")
            raise

    def verify_column_sorted(self, locator: Union[tuple, WebElement], column: Union[str, int], expected_order='ascending', strip_spaces=True, element_desc=None):
        logging.debug(f"{self.__class__.__name__}: Verifying column '{column}' is sorted in {expected_order} order")
        try:
            table_element = self.wait_for_element(locator, element_desc=element_desc) if isinstance(locator, tuple) else locator
            table_desc = element_desc or self._get_element_description(table_element)
            self.table_verifier.verify_column_sorted(table_element, column, expected_order, strip_spaces)
            logging.debug(f"{self.__class__.__name__}: Column sorting verification completed successfully for table: {table_desc}, column: {column}")
        except Exception as e:
            logging.error(f"{self.__class__.__name__}: Error verifying column sorting: {str(e)}")
            raise

    def select_table_row_checkbox(self, locator: Union[tuple, WebElement], identifier_column: Union[str, int], identifier_value: str, checkbox_column: int = 1, element_desc=None):
        logging.debug(f"{self.__class__.__name__}: Selecting checkbox for row with {identifier_column}: {identifier_value}")
        try:
            table_element = self.wait_for_element(locator, element_desc=element_desc) if isinstance(locator, tuple) else locator
            table_desc = element_desc or self._get_element_description(table_element)
            self.table_verifier.select_table_row_checkbox(table_element, identifier_column, identifier_value, checkbox_column)
            logging.debug(f"{self.__class__.__name__}: Checkbox selected successfully for row with {identifier_column}: {identifier_value} in table: {table_desc}")
        except Exception as e:
            logging.error(f"{self.__class__.__name__}: Error selecting checkbox: {str(e)}")
            raise

    def select_multiple_table_row_checkboxes(self, locator: Union[tuple, WebElement], identifier_column: Union[str, int], identifier_values: List[str], checkbox_column: int = 1, element_desc=None):
        logging.debug(f"{self.__class__.__name__}: Selecting checkboxes for multiple rows with {identifier_column}: {identifier_values}")
        try:
            table_element = self.wait_for_element(locator, element_desc=element_desc) if isinstance(locator, tuple) else locator
            table_desc = element_desc or self._get_element_description(table_element)
            self.table_verifier.select_multiple_table_row_checkboxes(table_element, identifier_column, identifier_values, checkbox_column)
            logging.debug(f"{self.__class__.__name__}: Checkboxes selected successfully for rows with {identifier_column}: {identifier_values} in table: {table_desc}")
        except Exception as e:
            logging.error(f"{self.__class__.__name__}: Error selecting multiple checkboxes: {str(e)}")
            raise