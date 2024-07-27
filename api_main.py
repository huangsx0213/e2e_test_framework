from robot.reporting import ResultWriter

from libraries.api.robot_cases_generator import APITestExecutor


def run_test_suite(suite):
    # Run the test suite and generate output XML
    suite.run(output='output.xml')

    # Generate log and report
    ResultWriter('output.xml').write_results(
        report='report.html',
        log='log.html'
    )


if __name__ == "__main__":
    te = APITestExecutor()
    # Create and run the test suite
    suite = te.create_test_suite(['TC001', 'TC002','TC003'], ['tag1'])
    run_test_suite(suite)