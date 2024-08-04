from robot.reporting import ResultWriter
from libraries.e2e.e2e_robot_generator import E2ERobotCasesGenerator


def run_test_suite(suite):
    # Run the test suite and generate output XML
    suite.run(output='output/output.xml')

    # Generate log and report
    ResultWriter('output/output.xml').write_results(
        report='output/report.html',
        log='output/log.html'
    )



if __name__ == "__main__":
    rcg = E2ERobotCasesGenerator()
    # Create and run the test suite
    suite = rcg.create_test_suite()
    run_test_suite(suite)

