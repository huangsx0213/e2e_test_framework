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
        """Generate performance reports."""
        if not self.tester:
            raise ValueError("Tester is not initialized.")
        self.tester.generate_reports()

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