import os
import argparse

from robot.libraries.BuiltIn import BuiltIn
from robot.reporting import ResultWriter
from libraries.common.utility_helpers import PROJECT_ROOT
from libraries.robot.robot_dashboard_generator import DashboardGenerator
from libraries.web.web_robot_generator import WebUIRobotCasesGenerator
from libraries.e2e.e2e_robot_generator import E2ERobotCasesGenerator
from libraries.api.api_robot_generator import APIRobotCasesGenerator


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


def create_api_suite():
    rcg = APIRobotCasesGenerator()
    return rcg.create_test_suite()


def create_web_suite():
    rcg = WebUIRobotCasesGenerator()
    return rcg.create_test_suite()


def create_e2e_suite():
    rcg = E2ERobotCasesGenerator()
    return rcg.create_test_suite()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run API, Web UI, or E2E tests.')
    parser.add_argument('--api', action='store_true', help='Run API tests')
    parser.add_argument('--web', action='store_true', help='Run Web UI tests')
    parser.add_argument('--e2e', action='store_true', help='Run E2E tests')
    args = parser.parse_args()

    if args.api:
        suite_to_run = create_api_suite()
    elif args.web:
        suite_to_run = create_web_suite()
    elif args.e2e:
        suite_to_run = create_e2e_suite()
    else:
        suite_to_run = create_e2e_suite()

    run_test_suite(suite_to_run)
