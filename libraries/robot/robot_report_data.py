import pandas as pd


class ReportData:

    def __init__(self):
        pass

    @classmethod
    def get_suite_statistics(self, suite_list):
        suite_data_frame = pd.DataFrame.from_records(suite_list)
        suite_stats = {
            "Total": suite_data_frame.Name.count(),
            "Pass": (suite_data_frame.Status == 'PASS').sum(),
            "Fail": (suite_data_frame.Status == 'FAIL').sum(),
            "Skip": (suite_data_frame.Status == 'SKIP').sum(),
            "Time": suite_data_frame.Time.sum(),
            "Min": suite_data_frame.Time.min(),
            "Max": suite_data_frame.Time.max(),
            "Avg": suite_data_frame.Time.mean()
        }
        return suite_stats

    @classmethod
    def get_test_statistics(self, test_list):
        test_data_frame = pd.DataFrame.from_records(test_list)
        test_stats = {
            "Total": test_data_frame.Status.count(),
            "Pass": (test_data_frame.Status == 'PASS').sum(),
            "Fail": (test_data_frame.Status == 'FAIL').sum(),
            "Skip": (test_data_frame.Status == 'SKIP').sum(),
            "Time": test_data_frame.Time.sum(),
            "Min": test_data_frame.Time.min(),
            "Max": test_data_frame.Time.max(),
            "Avg": test_data_frame.Time.mean()
        }
        return test_stats
