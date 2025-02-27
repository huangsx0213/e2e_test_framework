import os
import codecs
from robot.api import ExecutionResult
from jinja2 import Environment, FileSystemLoader

from libraries.robot.report.robot_result_visitor import CustomResultVisitor
from libraries.robot.report.robot_report_data import ReportData
from libraries.common.utility_helpers import PROJECT_ROOT


class DashboardGenerator:
    def __init__(self):
        self.result = None
        self.visitor = CustomResultVisitor()
        self.suite_list = []
        self.test_list = []
        self.suite_stats = {}
        self.test_stats = {}

    def _load_data(self, robot_output_path):
        self.result = ExecutionResult(robot_output_path)
        self.result.visit(self.visitor)
        self.suite_list = self.visitor.suite_list
        self.test_list = self.visitor.test_list
        report_data = ReportData()
        self.suite_stats = report_data.get_suite_statistics(self.suite_list)
        self.test_stats = report_data.get_test_statistics(self.test_list)

    def generate_dashboard(self, robot_output_path):
        self._load_data(robot_output_path)
        result_file_name = 'dashboard.html'
        result_file_directory = os.path.join(PROJECT_ROOT, 'report')
        os.makedirs(result_file_directory, exist_ok=True)
        result_file_path = os.path.join(result_file_directory, result_file_name)
        templates_dir = os.path.join(PROJECT_ROOT, 'templates')
        file_loader = FileSystemLoader(templates_dir)
        env = Environment(loader=file_loader)
        template = env.get_template('rf_report_template.html')
        with codecs.open(result_file_path, 'w', 'utf-8') as fh:
            fh.write(template.render(
                suite_stats=self.suite_stats,
                test_stats=self.test_stats,
                suites=self.suite_list,
                tests=self.test_list,
            ))


if __name__ == '__main__':
    # Example usage:
    generator = DashboardGenerator()
    generator.generate_dashboard(os.path.join(PROJECT_ROOT, 'report', 'output.xml'))
