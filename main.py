import os
import argparse
from robot.libraries.BuiltIn import BuiltIn
from robot.reporting import ResultWriter
from libraries.common.utility_helpers import PROJECT_ROOT
from libraries.robot.report.summary_report_generator import SummaryReportGenerator
from libraries.robot.report.robot_dashboard_generator import DashboardGenerator
from libraries.robot.case.unified_generator import UnifiedRobotCaseGenerator
from libraries.common.log_manager import logger_instance


class ExitOnFailureListener:
    ROBOT_LISTENER_API_VERSION = 3

    def __init__(self):
        self.exit_on_failure = False

    def end_test(self, data, result):
        if 'sanity check' in [tag.lower() for tag in result.tags] and result.status == 'FAIL':
            self.exit_on_failure = True
            BuiltIn().set_global_variable('${skip_on_sanity_check_failure}', True)


def run_test_suite(suite):
    listener = ExitOnFailureListener()
    output_dir = os.path.join(PROJECT_ROOT, 'report')
    output_xml = os.path.join(output_dir, 'output.xml')
    report_file = os.path.join(output_dir, 'report.html')
    log_file = os.path.join(output_dir, 'log.html')

    suite.run(output=output_xml, listener=listener)

    ResultWriter(output_xml).write_results(report=report_file, log=log_file)

    dashboard_generator = DashboardGenerator()
    dashboard_generator.generate_dashboard(output_xml)

    report_generator = SummaryReportGenerator(output_xml)
    report_generator.generate_html_report()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run API, Web UI, or E2E tests.')
    parser.add_argument('--api', action='store_true', help='Run API tests')
    parser.add_argument('--web', action='store_true', help='Run Web UI tests')
    parser.add_argument('--e2e', action='store_true', help='Run E2E tests')
    parser.add_argument('--performance', action='store_true', help='Run performance tests')
    args = parser.parse_args()

    default_test_type = 'e2e'
    if args.api:
        robot_case_generator = UnifiedRobotCaseGenerator('api')
    elif args.web:
        robot_case_generator = UnifiedRobotCaseGenerator('web')
    elif args.e2e:
        robot_case_generator = UnifiedRobotCaseGenerator('e2e')
    elif args.performance:
        robot_case_generator = UnifiedRobotCaseGenerator('performance')
    else:
        robot_case_generator = UnifiedRobotCaseGenerator(default_test_type)

    suite_to_run = robot_case_generator.generate_test_cases()
    run_test_suite(suite_to_run)

