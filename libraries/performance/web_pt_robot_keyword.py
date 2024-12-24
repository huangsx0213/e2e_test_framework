from robot.api import logger
from libraries.performance.web_pt import WebPerformanceTester

class RobotFrameworkWebTester:
    ROBOT_LIBRARY_SCOPE = 'TEST SUITE'
    def __init__(self):
        self.tester = None

    def initialize_tester(self, test_config_path=None, test_cases_path=None):
        """Initialize the performance tester."""
        self.tester = WebPerformanceTester(test_config_path, test_cases_path)
        logger.info("Performance tester initialized successfully.")

    def execute_single_test(self, case_id: str):
        """Execute a single performance test case."""
        if not self.tester:
            raise ValueError("Tester is not initialized.")
        self.tester.execute_single_test(case_id)

    def generate_reports(self, case_id: str):
        """Generate performance reports (charts and tables) for a specific case."""
        if not self.tester:
            raise ValueError("Tester is not initialized.")

        report_data = self.tester.generate_reports(case_id)

        logger.info('<h2>Memory Usage Trend Chart</h2>', html=True)
        logger.info(f'<img src="data:image/png;base64,{report_data["memory_chart"]}" alt="Memory Usage Trend"/>', html=True)

        logger.info('<h2>Response Time Statistics Chart</h2>', html=True)
        logger.info(f'<img src="data:image/png;base64,{report_data["response_time_stats_chart"]}" alt="Response Time Statistics"/>', html=True)

        logger.info('<h2>Response Time Trend Chart</h2>', html=True)
        logger.info(f'<img src="data:image/png;base64,{report_data["response_time_trend_chart"]}" alt="Response Time Trend"/>', html=True)

        logger.info('<h2>Response Time Statistics Table</h2>', html=True)
        logger.info(f'<img src="data:image/png;base64,{report_data["response_time_table"]}" alt="Response Time Statistics Table"/>', html=True)


    def finalize_and_close_tester(self):
        """Finalize the test by saving data to CSV, then close the tester and release resources."""
        if self.tester:
            self.tester.save_to_csv()
            self.tester.close()
            logger.info("Tester finalized and closed successfully.")