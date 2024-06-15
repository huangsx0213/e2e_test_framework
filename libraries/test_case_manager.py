import os
import re
import json
import pandas as pd
from collections import defaultdict
from libraries import logger


class TestCaseManager:
    def __init__(self, file_path, endpoints, headers_dir, template_dir, body_defaults_dir):
        self.file_path = file_path
        self.endpoints = endpoints
        self.headers_dir = headers_dir
        self.template_dir = template_dir
        self.body_defaults_dir = body_defaults_dir
        self.test_cases_df = None
        self.test_cases = self._read_test_cases()

    def _read_test_cases(self):
        test_cases_df = pd.read_excel(self.file_path, sheet_name='Active')
        test_cases_df = test_cases_df.fillna("")
        self.test_cases_df = test_cases_df
        test_cases = defaultdict(list)

        for _, row in test_cases_df.iterrows():
            tcid = row.get('TCID', "")
            test_step = {
                "TCID": tcid,
                "TSID": row.get('TSID', ""),
                "Descriptions": row.get('Descriptions', ""),
                "Conditions": row.get('Conditions', ""),
                "Endpoint": row.get('Endpoint', ""),
                "Headers": row.get('Headers', ""),
                "Template": row.get('Template', ""),
                "Defaults": row.get('Defaults', ""),
                "Body Modifications": row.get('Body Modifications') if row.get('Body Modifications') else '{}',
                "Run": row.get('Run', ""),
                "Tags": row.get('Tags', ""),
                "Exp Status": row.get('Exp Status', ""),
                "Exp Result": row.get('Exp Result', ""),
                "Save Fields": row.get('Save Fields', ""),
                "Act Status": row.get('Act Status', ""),
                "Act Result": row.get('Act Result', ""),
                "Result": row.get('Result', ""),
                "Saved Fields": row.get('Saved Fields', "")
            }
            # Validation
            self._validate_test_step(test_step, test_cases)

            test_cases[tcid].append(test_step)

        return test_cases

    def _validate_test_step(self, test_step, test_cases):
        try:
            if not test_step["TCID"]:
                raise ValueError("TCID is required")
            if not test_step["TSID"]:
                raise ValueError("TSID is required")
            if not test_step["Endpoint"]:
                raise ValueError("Endpoint is required")
            if not test_step["Headers"]:
                raise ValueError("Headers is required")

            if test_step["Conditions"]:
                conditions = test_step["Conditions"].splitlines()
                for condition in conditions:
                    if not any(x in condition for x in
                               ["[suite setup]", "[test setup]", "[suite teardown]", "[test teardown]"]):
                        raise ValueError(f"Condition '{condition}' is invalid")
                    referenced_tcid = condition.split("]")[1].strip()
                    if referenced_tcid not in test_cases:
                        raise ValueError(
                            f"Referenced TCID '{referenced_tcid}' in condition '{condition}' does not exist")

            if test_step["Headers"] and not self._file_exists_in_dir(test_step["Headers"], self.headers_dir, "json"):
                raise ValueError(f"Headers file '{test_step['Headers']}' does not exist in {self.headers_dir}")

            if test_step["Template"] and not self._file_exists_in_dir(test_step["Template"], self.template_dir,
                                                                      ["json", "xml"]):
                raise ValueError(f"Template file '{test_step['Template']}' does not exist in {self.template_dir}")

            if test_step["Defaults"] and not self._file_exists_in_dir(test_step["Defaults"], self.body_defaults_dir,
                                                                      "json"):
                raise ValueError(f"Defaults file '{test_step['Defaults']}' does not exist in {self.body_defaults_dir}")

            if test_step["Endpoint"] and test_step["Endpoint"] not in self.endpoints:
                raise ValueError(f"Endpoint '{test_step['Endpoint']}' does not exist in the configuration")

            if test_step["Body Modifications"] and not self._is_valid_body_modifications(
                    test_step["Body Modifications"]):
                raise ValueError("Body Modifications must be a valid JSON or contain valid placeholders")

            if test_step["Run"] not in ["Y", "N"]:
                raise ValueError("Run must be 'Y' or 'N'")

            if test_step["Tags"] and not self._is_valid_tag_format(test_step["Tags"]):
                raise ValueError("Tags format is invalid")

            if test_step["Exp Status"] and not self._is_valid_http_status(test_step["Exp Status"]):
                raise ValueError("Exp Status must be a valid HTTP status code")

            if test_step["Exp Result"] and not self._is_valid_exp_result_format(test_step["Exp Result"]):
                raise ValueError("Exp Result format is invalid")

            if test_step["Save Fields"] and not self._is_valid_save_fields_format(test_step["Save Fields"]):
                raise ValueError("Save Fields format is invalid")
            logger.info(f"Validation passed in test step {test_step['TSID']}")
        except ValueError as e:
            logger.error(f"Validation error in test step {test_step['TSID']}: {str(e)}")
            raise

    def _file_exists_in_dir(self, file_name, dir_path, extensions):
        if isinstance(extensions, str):
            extensions = [extensions]
        for ext in extensions:
            if os.path.exists(os.path.join(dir_path, f"{file_name}.{ext}")):
                return True
        return False

    def _is_valid_tag_format(self, tags: str) -> bool:
        # Example tag format validation: tags should be comma separated and non-empty
        return all(tag.strip() for tag in tags.split(','))

    def _is_valid_http_status(self, status: str) -> bool:
        try:
            status_code = int(status)
            return 100 <= status_code <= 599
        except ValueError:
            return False

    def _is_valid_exp_result_format(self, exp_result: str) -> bool:
        # Example validation: exp_result should be in the format "field_path=expected_value"
        lines = exp_result.splitlines()
        for line in lines:
            if '=' not in line:
                return False
            field_path, expected_value = line.split('=')
            if not self._is_valid_field_path(field_path.strip()):
                return False
        return True

    def _is_valid_save_fields_format(self, save_fields: str) -> bool:
        # Example validation: save_fields should be in the format "field_path"
        lines = save_fields.splitlines()
        for line in lines:
            if not self._is_valid_field_path(line.strip()):
                return False
        return True

    def _is_valid_field_path(self, field_path: str) -> bool:
        # Validation rule: field_path should be separated by dots and should not contain spaces around dots
        return re.match(r'^[a-zA-Z0-9_\[\]]+(\.[a-zA-Z0-9_\[\]]+)*$', field_path) is not None

    def _is_valid_body_modifications(self, body_modifications: str) -> bool:
        # Allow JSON with ${...} placeholders
        try:
            # Replace placeholders with a dummy value for JSON validation
            modified_body = re.sub(r'\$\{[^}]+\}', '0', body_modifications)
            json.loads(modified_body)
            return True
        except json.JSONDecodeError:
            return False

    def get_conditions_by_tc_id(self, tcid: str):
        return self.test_cases.get(tcid, None)

    def filter_test_cases(self, tcid_list=None, tags=None):
        filtered = defaultdict(list)
        for tcid, test_steps in self.test_cases.items():
            if tcid_list and tcid not in tcid_list:
                continue
            for test_step in test_steps:
                if test_step['Run'].upper() != 'Y':
                    continue
                if tags and not any(tag in test_step['Tags'] for tag in tags):
                    continue
                filtered[tcid].append(test_step)
        return filtered

    def get_row_index_by_tsid(self, tsid):
        try:
            tsid_list = self.test_cases_df['TSID'].tolist()
            index = tsid_list.index(tsid)
            return index
        except ValueError:
            return None
