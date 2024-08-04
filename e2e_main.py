import os
from robot.reporting import ResultWriter
from libraries.common.utility_helpers import PROJECT_ROOT
from libraries.e2e.e2e_robot_generator import E2ERobotCasesGenerator


def run_test_suite(suite):
    # Run the test suite and generate output XML
    output_xml = os.path.join(PROJECT_ROOT, 'output', 'output.xml')
    report_file = os.path.join(PROJECT_ROOT, 'output', 'report.html')
    log_file = os.path.join(PROJECT_ROOT, 'output', 'log.html')
    suite.run(output=output_xml)

    # Generate log and report
    ResultWriter(output_xml).write_results(
        report=report_file,
        log=log_file
    )



if __name__ == "__main__":
    rcg = E2ERobotCasesGenerator()
    # Create and run the test suite
    suite = rcg.create_test_suite()
    run_test_suite(suite)

