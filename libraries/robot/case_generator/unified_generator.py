from libraries.robot.case_generator.api_generator import APIRobotCaseGenerator
from libraries.robot.case_generator.e2e_generator import E2ERobotCaseGenerator
from libraries.robot.case_generator.web_generator import WebRobotCaseGenerator

class RobotCaseGeneratorFactory:
    @staticmethod
    def get_generator(test_type):
        if test_type == "api":
            return APIRobotCaseGenerator()
        elif test_type == "web":
            return WebRobotCaseGenerator()
        elif test_type == "e2e":
            return E2ERobotCaseGenerator()
        else:
            raise ValueError(f"Unsupported test type: {test_type}")

class UnifiedRobotCaseGenerator:
    def __init__(self, test_type):
        self.generator = RobotCaseGeneratorFactory.get_generator(test_type)

    def generate_test_cases(self, tc_id_list=None, tags=None):
        self.generator.load_configuration()
        self.generator.initialize_components()
        suite = self.generator.create_test_suite(tc_id_list, tags)
        return suite