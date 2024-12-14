import logging
import re
import yaml
from typing import Dict, Any
import pandas as pd
from libraries.common.utility_helpers import UtilityHelpers
from libraries.api.variable_generator import VariableGenerator
from robot.libraries.BuiltIn import BuiltIn

builtin_lib = BuiltIn()


class HeadersGenerator:
    def __init__(self, api_test_loader) -> None:
        self.format_json = UtilityHelpers.format_json
        self.api_test_loader = api_test_loader

    def prepare_headers(self, testcase, saved_fields):
        try:
            headers_name = testcase['Headers']
            headers = self.api_test_loader.get_headers()

            # Ensure headers_name exists and is valid
            if headers_name not in headers['HeaderName'].values:
                raise ValueError(f"Headers name '{headers_name}' not found in the headers dataframe.")

            # Convert to string explicitly before checking
            header_content = str(headers[headers['HeaderName'] == headers_name]['Content'].iloc[0])
            logging.info(f"{self.__class__.__name__}: Headers for test case '{testcase['TCID']}' loaded from file: \n{header_content}")

            # Check if header_content is empty
            if pd.isna(header_content):
                raise ValueError("Header content is empty.")

            # Parse the YAML-like content
            original_headers = yaml.safe_load(header_content)

            headers = {k: self.replace_placeholders(v, saved_fields, testcase) for k, v in original_headers.items()}
            logging.info(f"{self.__class__.__name__}: Headers for test case '{testcase['TCID']}' replaced placeholders: \n{self.format_json(headers)}")

            return headers

        except KeyError as e:
            logging.error(f"{self.__class__.__name__}: Headers file '{headers_name}' not found in test case '{testcase['TCID']}': {str(e)}")
            raise

        except yaml.YAMLError as e:
            logging.error(f"{self.__class__.__name__}: Invalid YAML format in headers file '{headers_name}' for test case '{testcase['TCID']}': {str(e)}")
            raise

        except pd.errors.EmptyDataError as e:
            logging.error(f"{self.__class__.__name__}: No data found in headers dataframe: {str(e)}")
            raise

        except TypeError as e:
            logging.error(f"{self.__class__.__name__}: TypeError when parsing YAML content for headers file '{headers_name}' for test case '{testcase['TCID']}': {str(e)}")
            raise

        except Exception as e:
            logging.error(f"{self.__class__.__name__}: Error processing headers file '{headers_name}' for test case '{testcase['TCID']}': {str(e)}")
            raise

    def replace_placeholders(self, value: Any, saved_fields: Dict[str, Any], testcase) -> Any:
        headers_filename = testcase['Headers']
        try:
            if isinstance(value, str):
                # Replace {{...}}
                value = re.sub(r'\{\{\s*([^}]+?)\s*\}\}', lambda m: self._get_placeholder_value(m.group(1), saved_fields, testcase), value,
                               flags=re.DOTALL | re.MULTILINE)

                # Replace ${...}
                value = re.sub(r'\$\{([^}]+)\}', lambda m: str(builtin_lib.get_variable_value('${' + m.group(1) + '}')), value, flags=re.DOTALL | re.MULTILINE)

                # Logging for ${...} replacements
                for match in re.findall(r'\$\{([^}]+)\}', value):
                    replacement_value = builtin_lib.get_variable_value(f'${{{match}}}')
                    logging.info(f"{self.__class__.__name__}:Replaced ${{{match}}} with variable value '{replacement_value}' for test case '{testcase['TCID']}'")

            return value
        except Exception as e:
            logging.error(
                f"{self.__class__.__name__}:Unexpected error replacing placeholders in headers file '{headers_filename}' for test case '{testcase['TCID']}': {str(e)}"
            )
            raise

    def _get_placeholder_value(self, placeholder: str, saved_fields: Dict[str, Any], testcase: Dict[str, Any]) -> str:
        if placeholder in saved_fields:
            value = str(saved_fields[placeholder])
            logging.info(f"{self.__class__.__name__}:Replaced {{{{{placeholder}}}}} with saved field '{value}' for test case '{testcase['TCID']}'")
        else:
            try:
                value = str(VariableGenerator.generate_dynamic_value(placeholder))
                logging.info(f"{self.__class__.__name__}:Replaced {{{{{placeholder}}}}} with dynamic value '{value}' for test case '{testcase['TCID']}'")
            except Exception as e:
                logging.warning(f"{self.__class__.__name__}:Failed to generate dynamic value for {{{{{placeholder}}}}} in test case '{testcase['TCID']}': {str(e)}")
                value = f"{{{{UNKNOWN_PLACEHOLDER_{placeholder}}}}}"
        return value
