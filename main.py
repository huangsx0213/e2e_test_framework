import os
import argparse
from robot.api import TestSuite
from robot.reporting import ResultWriter
from libraries.common.utility_helpers import PROJECT_ROOT
from libraries.api.api_robot_generator import APIRobotCasesGenerator
from libraries.web.web_robot_generator import WebUIRobotCasesGenerator
from libraries.e2e.e2e_robot_generator import E2ERobotCasesGenerator

def run_test_suite(suite):
    # Run the test suite and generate report XML
    output_xml = os.path.join(PROJECT_ROOT, 'report', 'output.xml')
    report_file = os.path.join(PROJECT_ROOT, 'report', 'report.html')
    log_file = os.path.join(PROJECT_ROOT, 'report', 'log.html')
    suite.run(output=output_xml)

    # Generate log and report
    ResultWriter(output_xml).write_results(
        report=report_file,
        log=log_file
    )

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
    if args.web:
        suite_to_run = create_web_suite()
    if args.e2e:
        suite_to_run = create_e2e_suite()

    # If no specific test type is specified, run default E2E tests
    if not (args.api or args.web or args.e2e):
        suite_to_run = create_e2e_suite()

    run_test_suite(suite_to_run)