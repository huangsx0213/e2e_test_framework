from abc import ABC, abstractmethod

class RobotCaseGenerator(ABC):
    @abstractmethod
    def load_configuration(self):
        pass

    @abstractmethod
    def initialize_components(self):
        pass

    @abstractmethod
    def create_test_suite(self, tc_id_list=None, tags=None, parent_suite=None):
        pass

    @abstractmethod
    def create_test_case(self, suite, test_case):
        pass

    @abstractmethod
    def create_test_steps(self, robot_test, test_steps, data_set):
        pass