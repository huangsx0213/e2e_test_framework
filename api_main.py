from libraries.api.api_test_executor import APITestExecutor

if __name__ == "__main__":
    api_requester = APITestExecutor()
    api_requester.run_test_suite()
