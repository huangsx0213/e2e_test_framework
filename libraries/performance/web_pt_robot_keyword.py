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

    def execute_tests(self):
        """Execute performance tests."""
        if not self.tester:
            raise ValueError("Tester is not initialized.")
        self.tester.execute_tests()

    def generate_reports(self):
        """Generate performance reports (charts and tables)."""
        if not self.tester:
            raise ValueError("Tester is not initialized.")

        memory_chart = self.tester.generate_memory_usage_chart()
        response_time_stats_chart = self.tester.generate_response_time_statistics_chart()
        response_time_trend_chart = self.tester.generate_response_time_trend_chart()
        response_time_table = self.tester.generate_response_time_statistics_table()

        logger.info('<h2>Memory Usage Trend Chart</h2>', html=True)
        logger.info(f'<img src="data:image/png;base64,{memory_chart}" alt="Memory Usage Trend"/>', html=True)

        logger.info('<h2>Response Time Statistics Chart</h2>', html=True)
        logger.info(f'<img src="data:image/png;base64,{response_time_stats_chart}" alt="Response Time Statistics"/>', html=True)

        logger.info('<h2>Response Time Trend Chart</h2>', html=True)
        logger.info(f'<img src="data:image/png;base64,{response_time_trend_chart}" alt="Response Time Trend"/>', html=True)

        logger.info('<h2>Response Time Statistics Table</h2>', html=True)
        logger.info(f'<img src="data:image/png;base64,{response_time_table}" alt="Response Time Statistics Table"/>', html=True)

    def save_to_csv(self):
        """Save test data (response time and memory usage) to CSV files."""
        if self.tester:
            self.tester.save_to_csv()

    def save_to_csv(self):
        """Save test data to CSV files."""
        if not self.tester:
            raise ValueError("Tester is not initialized.")
        self.tester.save_to_csv()

    def close_tester(self):
        """Close the tester and release resources."""
        if self.tester:
            self.tester.close()
            logger.info("Tester closed successfully.")