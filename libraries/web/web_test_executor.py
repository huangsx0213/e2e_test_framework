from time import sleep
from libraries.common.log_manager import logger
from libraries.web.web_test_loader import WebTestLoader
from libraries.web.page_object import PageObject
from libraries.common.utility_helpers import PROJECT_ROOT


class WebTestExecutor:
    def __init__(self, driver, test_case_path):
        self.driver = driver
        self.web_test_loader = WebTestLoader(test_case_path)
        self.page_object = PageObject(
            driver,
            self.web_test_loader.get_locators(),
            self.web_test_loader.get_page_objects()
        )
        self.project_root: str = PROJECT_ROOT


    def run_tests(self):
        test_cases = self.web_test_loader.get_test_cases()
        for _, test_case in test_cases.iterrows():
            case_id = test_case['Case ID']
            if test_case['Run'] == 'Y':
                try:
                    self.run_test_case(case_id)
                except Exception as e:
                    logger.error(f"Error running test case {case_id}: {str(e)}")
                sleep(1)

    def run_test_case(self, case_id):
        logger.info(f"Starting E2E test case {case_id}")
        test_steps = self.web_test_loader.get_test_steps(case_id)
        test_data_sets = self.web_test_loader.get_test_data(case_id)

        for data_set_index, data_set in enumerate(test_data_sets, 1):
            logger.info(f"Running E2E test case {case_id} with data set {data_set_index}")
            for _, step in test_steps.iterrows():
                page_name = step['Page Name']
                module_name = step['Module Name']
                parameters = self._get_parameters(data_set, step['Parameter Name'])

                try:
                    logger.info(f"Executing web step: {page_name}.{module_name}")
                    self.page_object.execute_module(page_name, module_name, parameters)
                except Exception as e:
                    logger.error(f"Error executing step {page_name}.{module_name}: {str(e)}")
                    raise

            logger.info(f"Completed E2E test case {case_id} with data set {data_set_index}")
            sleep(1)  # Add a small delay between data sets

    def _get_parameters(self, data_set, parameter_names):
        parameters = {}
        for name in parameter_names.split(','):
            if name in data_set:
                parameters[name] = data_set[name]
        logger.debug(f"Extracted parameters: {parameters}")
        return parameters