from robot.api import ResultVisitor


class CustomResultVisitor(ResultVisitor):

    def __init__(self):
        self.suite_list = []
        self.test_list = []

    def start_suite(self, suite):
        if suite.tests:
            try:
                stats = suite.statistics.all
            except:
                stats = suite.statistics

            try:
                skipped = stats.skipped
            except:
                skipped = 0

            suite_json = {
                "Name": suite.longname,
                "Id": suite.id,
                "Status": suite.status,
                "Total": stats.total,
                "Pass": stats.passed,
                "Fail": stats.failed,
                "Skip": skipped,
                "startTime": suite.starttime,
                "endTime": suite.endtime,
                "Time": suite.elapsedtime
            }
            self.suite_list.append(suite_json)

    def visit_test(self, test):
        test_json = {
            "Suite Name": test.parent.longname,
            "Suite Id": test.parent.id,
            "Test Name": test.name,
            "Test Id": test.id,
            "Status": test.status,
            "startTime": test.starttime,
            "endTime": test.endtime,
            "Time": test.elapsedtime,
            "Message": test.message,
            "Tags": test.tags
        }
        self.test_list.append(test_json)
