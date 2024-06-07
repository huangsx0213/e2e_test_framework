import pandas as pd
from collections import defaultdict
import pprint


class TestCaseManager:
    def __init__(self, file_path):
        self.file_path = file_path
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
                "Body Modifications": row.get('Body Modifications', ""),
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
            test_cases[tcid].append(test_step)

        return test_cases

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