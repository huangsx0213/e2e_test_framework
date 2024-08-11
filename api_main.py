import os
from robot.reporting import ResultWriter
from libraries.api.api_robot_generator import APIRobotCasesGenerator
from libraries.common.utility_helpers import PROJECT_ROOT


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


if __name__ == "__main__":
    rcg = APIRobotCasesGenerator()
    # Create and run the test suite
    suite = rcg.create_test_suite()
    run_test_suite(suite)
