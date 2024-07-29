from robot.reporting import ResultWriter

from libraries.api.robot_cases_generator import APITestExecutor


def run_test_suite(suite):
    # Run the test suite and generate output XML
    suite.run(output='output/output.xml')

    # Generate log and report
    ResultWriter('output/output.xml').write_results(
        report='output/report.html',
        log='output/log.html'
    )


if __name__ == "__main__":
    te = APITestExecutor()
    # Create and run the test suite
    suite = te.create_test_suite()
    run_test_suite(suite)