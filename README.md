
# Automated Testing Framework User Manual

## Table of Contents
1. Installation and Setup
2. Configuration
3. Test Case Excel Structure
4. Writing Test Cases
5. Running Tests
6. Viewing Results
7. Best Practices
8. Troubleshooting
9. Advanced Features
10. Maintenance and Updates

## 1. Installation and Setup

### 1.1 Python and pip

Ensure you have Python 3.7 or higher installed. You can download it from [python.org](https://www.python.org/downloads/).

### 1.2 Required Python Packages

Install the required packages using pip:

```bash
pip install -r requirements.txt
```

The `requirements.txt` file should include (but is not limited to):

```
robot-framework
requests
pandas
openpyxl
pyyaml
jinja2
jsonpath-ng
lxml
selenium
```

### 1.3 WebDriver Setup

For Web UI testing, ensure you have the appropriate WebDriver installed and configured in your system PATH:
- ChromeDriver for Google Chrome
- EdgeDriver for Microsoft Edge

## 2. Configuration

### 2.1 API Test Configuration (api_test_config.yaml)

- `active_environment`: Set the active environment (e.g., DEV, SIT, UAT, PROD)
- `test_cases_path`: Specify the path to the Excel file containing API test cases
- `clear_saved_fields_after_test`: Set to true/false to clear saved fields after each test
- `tc_id_list`: List of specific Test Case IDs to run (leave empty to run all)
- `tags`: List of tags to filter test cases (leave empty to run all)

### 2.2 Web UI Test Configuration (web_test_config.yaml)

- `active_environment`: Set the active environment (e.g., DEV, SIT, UAT, PROD)
- `test_cases_path`: Specify the path to the Excel file containing Web UI test cases
- `tc_id_list`: List of specific Test Case IDs to run (leave empty to run all)
- `tags`: List of tags to filter test cases (leave empty to run all)

### 2.3 E2E Test Configuration (e2e_test_config.yaml)

- `active_environment`: Set the active environment (e.g., DEV, SIT, UAT, PROD)
- `test_cases_path`: Specify the path to the Excel file containing E2E test cases
- `tc_id_list`: List of specific Test Case IDs to run (leave empty to run all)
- `tags`: List of tags to filter test cases (leave empty to run all)

## 3. Test Case Excel Structure

### 3.1 API Test Cases Excel

#### Sheets:
1. API: Main test case information
2. BodyTemplates: Request body templates
3. BodyDefaults: Default values for request bodies
4. Headers: Header templates
5. Endpoints: Environment-specific endpoint configurations

#### API Sheet Columns:
- TCID: Unique test case ID
- Name: Test case name
- Descriptions: Test case description
- Run: 'Y' to include in test run, 'N' to exclude
- Tags: Comma-separated tags for filtering
- Endpoint: Endpoint name (must match Endpoints sheet)
- Headers: Header template name (must match Headers sheet)
- Body Template: Body template name (must match BodyTemplates sheet)
- Body Default: Default body name (must match BodyDefaults sheet)
- Body User-defined Fields: Custom fields for the request body (JSON format)
- Exp Result: Expected results (use JSONPath for assertions)
- Save Fields: Fields to save from the response (use JSONPath)
- Conditions: Special conditions (e.g., [Checkwith], [TestSetup], [TestTeardown])

### 3.2 Web UI Test Cases Excel

#### Sheets:
1. TestCases: Main test case information
2. TestSteps: Steps for each test case
3. TestData: Test data for parameterization
4. Locators: Element locators
5. PageModules: Page object definitions
6. WebEnvironments: Environment-specific configurations

#### TestCases Sheet Columns:
- Case ID: Unique test case ID
- Name: Test case name
- Descriptions: Test case description
- Run: 'Y' to include in test run, 'N' to exclude
- Tags: Comma-separated tags for filtering

#### TestSteps Sheet Columns:
- Case ID: Corresponding test case ID
- Step Order: Order of execution
- Page Name: Page object name
- Module Name: Module name within the page object
- Parameter Name: Comma-separated parameter names

#### TestData Sheet Columns:
- Case ID: Corresponding test case ID
- Data Set: Data set identifier
- Parameter Name: Name of the parameter
- Value: Value for the parameter

## 4. Writing Test Cases

### 4.1 API Test Cases

1. Fill in the API sheet with test case details.
2. Create body templates in the BodyTemplates sheet.
3. Define default body values in the BodyDefaults sheet.
4. Create header templates in the Headers sheet.
5. Define endpoints in the Endpoints sheet.

#### Body-related fields:
- Body Template: Use Jinja2 syntax for dynamic values.
- Body Default: Provide default values in JSON format.
- Body User-defined Fields: Override default values or add new fields in JSON format.
  - Supports dynamic values using `${variable_name}` syntax.
  - These variables are replaced with actual values from the Robot Framework variable scope.
- Use `{{variable_name}}` in templates for dynamic values.
- Supported dynamic values: uetr, uuid4, value_date, msg_id, timestamp, formated_timestamp, bic

#### Expected Results:
- Exp Result: Define expected results for assertions.
  - Supports dynamic values using `${variable_name}` syntax.
  - These variables are replaced with actual values from the Robot Framework variable scope.
- Use JSONPath for precise assertions on the response.

#### Headers:
- Define headers in YAML format in the Headers sheet.
- Use `{{variable_name}}` for dynamic values.
- Use `${variable_name}` for Robot Framework variables.

#### Example of using dynamic values:
```
Body User-defined Fields: {"user_id": "${USER_ID}", "timestamp": "{{timestamp}}"}
Exp Result: $.response.status=${EXPECTED_STATUS}
```

In this example:
- `${USER_ID}` will be replaced with the value of the USER_ID variable from the Robot Framework scope.
- `{{timestamp}}` will be replaced with a dynamically generated timestamp.
- `${EXPECTED_STATUS}` in the Exp Result will be replaced with the value of the EXPECTED_STATUS variable from the Robot Framework scope.

### 4.2 Web UI Test Cases

1. Fill in the TestCases sheet with test case details.
2. Define test steps in the TestSteps sheet.
3. Provide test data in the TestData sheet.
4. Define element locators in the Locators sheet.
5. Create page objects and modules in the PageModules sheet.
6. Configure environments in the WebEnvironments sheet.

## 5. Running Tests

### 5.1 API Tests
```bash
python e2e_main.py --api
```

### 5.2 Web UI Tests
```bash
python e2e_main.py --web
```

### 5.3 E2E Tests
```bash
python e2e_main.py --e2e
```



## 6. Viewing Results

- Test results are generated in the `report` folder.
- Open `report.html` for a detailed test report.
- Check `log.html` for step-by-step execution logs.
- Screenshots for Web UI tests are embedded in the logs.

## 7. Best Practices

1. Use meaningful test case IDs and names.
2. Leverage tags for easy filtering and organization.
3. Maintain clear and concise test step descriptions.
4. Regularly update and maintain test data.
5. Keep locators and page objects up-to-date with the application.
6. Use parameterization to create data-driven tests.
7. Implement proper error handling and logging in test scripts.
8. Regularly review and optimize test suites for efficiency.

## 8. Troubleshooting

- Check log files for detailed error messages.
- Verify configuration files for correct settings.
- Ensure all required dependencies are installed.
- Validate Excel file structure and content.
- Check for proper WebDriver setup for Web UI tests.
- If you encounter "ModuleNotFoundError", ensure you've installed all required packages (see Section 1.2).

## 9. Advanced Features

### 9.1 Dynamic Values in API Tests

The framework supports the use of dynamic values in two key areas of API tests:

1. Body User-defined Fields
2. Expected Results (Exp Result)

#### Usage:
- Use the syntax `${variable_name}` in these fields to reference Robot Framework variables.
- These variables will be dynamically replaced with their actual values during test execution.
- This feature allows for more flexible and reusable test cases, especially when combined with Robot Framework's variable management capabilities.

#### Example:
```yaml
Body User-defined Fields: {"token": "${AUTH_TOKEN}", "user_id": "${CURRENT_USER_ID}"}
Exp Result: $.status_code=200
$.response.user.name=${EXPECTED_USER_NAME}
```

In this example:
- `${AUTH_TOKEN}` and `${CURRENT_USER_ID}` in the Body User-defined Fields will be replaced with their respective values from the Robot Framework variable scope.
- `${EXPECTED_USER_NAME}` in the Exp Result will be replaced with the actual expected user name from the Robot Framework variable scope.

#### Benefits:
- Increased test case reusability across different environments or scenarios.
- Easier management of test data and expected results.
- Support for data-driven testing when combined with Robot Framework's variable files or command-line variable setting.

Remember to set these variables in your Robot Framework test suite setup, or pass them as arguments when running your tests for this feature to work effectively.

## 10. Maintenance and Updates

- Regularly update your Python packages to ensure compatibility and security:
  ```bash
  pip install --upgrade -r requirements.txt
  ```
- Keep your WebDrivers up-to-date with your browser versions.
- Periodically review and update your test cases to align with application changes.
- Consider version controlling your test cases and configurations for better tracking and collaboration.
- Implement a process for reviewing and updating test data to ensure it remains relevant and effective.
- Regularly backup your test artifacts, including Excel files, configurations, and custom scripts.
- Set up automated jobs to run your test suites on a scheduled basis, ensuring continuous validation of your application.

This comprehensive guide provides a complete overview of the automated testing framework, including setup, configuration, test case creation, execution, and maintenance. It covers both API and Web UI testing scenarios, as well as advanced features like dynamic value handling in API tests. By following this guide, users should be able to effectively leverage the framework for their testing needs.