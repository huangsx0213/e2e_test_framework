# Automated Testing Framework User Manual

## Table of Contents
1. Framework Features
2. Installation and Setup
3. Configuration
4. API Test Cases Excel Structure
5. Web UI Test Cases Excel Structure
6. Writing Test Cases
7. Running Tests
8. Viewing Results
9. Best Practices
10. Troubleshooting
11. Advanced Features
12. Maintenance and Updates

## 1. Framework Features

This automated testing framework offers the following features:

1. Multi-type Testing Support: Supports API testing, Web UI testing, and End-to-End (E2E) testing.
2. Flexible Configuration: Uses YAML files for configuration, making it easy to modify and maintain.
3. Data-Driven: Manages test cases using Excel files, supporting parameterized testing.
4. Dynamic Value Support: Supports dynamically generated values in API tests, such as UUID, timestamps, etc.
5. Variable Management: Supports sharing and reusing variables between test cases.
6. Page Object Model: Uses page object pattern in Web UI testing, improving code reusability and maintainability.
7. Custom Operations: Supports defining and using custom Python operations in Web UI tests.
8. Detailed Logs and Reports: Generates detailed HTML reports and logs, including failure screenshots.
9. Flexible Test Case Selection: Supports filtering specific tests by tags or test case IDs.
10. Environment Management: Supports multi-environment configuration, making it easy to switch between different environments.
11. Error Handling and Retry Mechanism: Implements robust error handling and test retry logic.
12. CI-Friendly: Easy to integrate into CI/CD processes.
13. Extensibility: Modular framework design, easy to add new features and customize.
14. Sanity Check Feature: Supports automatic skipping of subsequent tests if a designated sanity check test fails.

## 2. Installation and Setup

### 2.1 Python and pip

Ensure you have Python 3.7 or higher installed. You can download it from [python.org](https://www.python.org/downloads/).

### 2.2 Required Python Packages

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
pillow
numpy
```

### 2.3 WebDriver Setup

For Web UI testing, ensure you have the appropriate WebDriver installed and configured in your system PATH:
- ChromeDriver for Google Chrome
- EdgeDriver for Microsoft Edge

### 2.4 Project Structure

Ensure your project follows this structure:
```
project_root/
├── configs/
│   ├── api_test_config.yaml
│   ├── web_test_config.yaml
│   ├── e2e_test_config.yaml
│   └── logging_config.yaml
├── libraries/
│   ├── api/
│   ├── web/
│   ├── e2e/
│   ├── robot/
│   └── common/
├── test_cases/
│   ├── api_test_cases.xlsx
│   ├── web_test_cases.xlsx
│   └── e2e_test_cases.xlsx
├── templates/
│   └── rf_report_template.html
├── report/
├── main.py
├── yaml_config_cli.py
└── requirements.txt
```

## 3. Configuration

### 3.1 API Test Configuration (api_test_config.yaml)

```yaml
active_environment: DEV
test_cases_path: 'test_cases/api_test_cases.xlsx'
clear_saved_fields_after_test: true
tc_id_list: []
tags: []
```

- `active_environment`: Currently active test environment (e.g., DEV, SIT, UAT, PROD)
- `test_cases_path`: Path to the API test cases Excel file
- `clear_saved_fields_after_test`: Whether to clear saved fields after each test
- `tc_id_list`: List of specific test case IDs to execute
- `tags`: List of tags to filter test cases

### 3.2 Web UI Test Configuration (web_test_config.yaml)

```yaml
active_environment: SIT
test_case_path: 'test_cases/web_test_cases.xlsx'
tc_id_list: []
tags: []
```

- `active_environment`: Currently active test environment
- `test_case_path`: Path to the Web UI test cases Excel file
- `tc_id_list`: List of specific test case IDs to execute
- `tags`: List of tags to filter test cases

### 3.3 End to end Test Configuration (e2e_test_config.yaml)

```yaml
active_environment: SIT
test_case_path: 'test_cases/e2e_test_cases.xlsx'
tc_id_list: []
tags: []
```

- `active_environment`: Currently active test environment
- `test_case_path`: Path to the End-to-End test cases Excel file
- `tc_id_list`: List of specific test case IDs to execute
- `tags`: List of tags to filter test cases
- 
### 3.4 Using yaml_config_cli.py

You can use the `yaml_config_cli.py` script to modify configuration files from the command line. For example:

```bash
python yaml_config_cli.py configs/api_test_config.yaml --update active_environment PROD
python yaml_config_cli.py configs/api_test_config.yaml --add-to-list tc_id_list TC001
python yaml_config_cli.py configs/api_test_config.yaml --remove-from-list tags deprecated
```

## 4. API Test Cases Excel Structure

### 4.1 Sheets:
1. API: Main test case information
2. BodyTemplates: Request body templates
3. BodyDefaults: Default values for request bodies
4. Headers: Header templates
5. Endpoints: Environment-specific endpoint configurations

### 4.2 API Sheet Columns:
| Column Name | Description | Possible Values | Logic |
|-------------|-------------|-----------------|-------|
| TCID | Unique test case identifier | String, e.g., "TC001" | Must be unique |
| Name | Test case name | String | Descriptive name |
| Descriptions | Test case description | String | Detailed explanation of test purpose |
| Run | Whether to execute this case | "Y" or "N" | Y means execute, N means skip |
| Tags | Case tags | Comma-separated string | For categorizing and filtering cases |
| Endpoint | API endpoint name | String | Must match definitions in Endpoints sheet |
| Headers | Request header template name | String | Must match definitions in Headers sheet |
| Body Template | Request body template name | String | Must match definitions in BodyTemplates sheet |
| Body Default | Default request body name | String | Must match definitions in BodyDefaults sheet |
| Body User-defined Fields | Custom request body fields | JSON format string | Overrides or adds to default request body |
| Exp Result | Expected results | JSONPath expressions | Used to validate response content |
| Save Fields | Save response fields | JSONPath expressions | Used to save specific fields from the response |
| Conditions | Special conditions | Specific format string | E.g., [Checkwith], [TestSetup], [TestTeardown] |
| Wait | Wait time after test execution | Number (seconds) | Pause execution for specified time |

#### Sanity Check:
To designate a test case as a sanity check:
1. In the 'Tags' column of the API sheet, include the tag 'sanity check' (case-insensitive).
2. If a test case with the 'sanity check' tag fails, all subsequent test cases will be automatically skipped.

Example:
```
TCID | Name           | ... | Tags
-----|----------------|-----|----------------
TC001| Sanity Check   | ... | critical, sanity check
TC002| Regular Test   | ... | regression
```

### 4.3 BodyTemplates Sheet:
| Column Name | Description | Possible Values | Logic |
|-------------|-------------|-----------------|-------|
| TemplateName | Template name | String | Unique identifier |
| Content | Template content | JSON or XML format string | Can include Jinja2 template syntax |
| Format | Template format | "json" or "xml" | Specifies the format of the template |

### 4.4 BodyDefaults Sheet:
| Column Name | Description | Possible Values | Logic |
|-------------|-------------|-----------------|-------|
| Name | Default value name | String | Unique identifier |
| Content | Default value content | JSON format string | Provides default request body content |

### 4.5 Headers Sheet:
| Column Name | Description | Possible Values | Logic |
|-------------|-------------|-----------------|-------|
| HeaderName | Header template name | String | Unique identifier |
| Content | Header content | YAML format string | Defines request headers |

### 4.6 Endpoints Sheet:
| Column Name | Description | Possible Values | Logic |
|-------------|-------------|-----------------|-------|
| Environment | Environment name | DEV, SIT, UAT, PROD, etc. | Corresponds to active_environment in config file |
| Endpoint | Endpoint name | String | Unique identifier |
| Method | HTTP method | GET, POST, PUT, DELETE, PATCH | Specifies request method |
| Path | Request path | URL path string | Can include path parameters |

## 5. Web UI Test Cases Excel Structure

### 5.1 Sheets:
1. TestCases: Main test case information
2. TestSteps: Steps for each test case
3. TestData: Test data for parameterization
4. Locators: Element locators
5. PageModules: Page object definitions
6. WebEnvironments: Environment-specific configurations
7. CustomActions: Custom Python actions

### 5.2 TestCases Sheet:
| Column Name | Description | Possible Values | Logic |
|-------------|-------------|-----------------|-------|
| Case ID | Unique test case identifier | String, e.g., "UITC001" | Must be unique |
| Name | Test case name | String | Descriptive name |
| Descriptions | Test case description | String | Detailed explanation of test purpose |
| Run | Whether to execute this case | "Y" or "N" | Y means execute, N means skip |
| Tags | Case tags | Comma-separated string | For categorizing and filtering cases |

#### Sanity Check:
To designate a test case as a sanity check:
1. In the 'Tags' column of the TestCases sheet, include the tag 'sanity check' (case-insensitive).
2. If a test case with the 'sanity check' tag fails, all subsequent test cases will be automatically skipped.

Example:
```
Case ID | Name           | ... | Tags
--------|----------------|-----|----------------
UITC001 | Sanity Check   | ... | critical, sanity check
UITC002 | Regular Test   | ... | regression
```

### 5.3 TestSteps Sheet:
| Column Name | Description | Possible Values | Logic |
|-------------|-------------|-----------------|-------|
| Case ID | Corresponding test case ID | String | Must match Case ID in TestCases |
| Step ID | Unique identifier for each step | Integer | Defines execution order of steps |
| Page Name | Page object name | String | Must match definitions in PageModules |
| Module Name | Module name | String | Specific module within the page object |
| Parameter Name | Parameter names | Comma-separated string | Corresponds to parameters in TestData |
| Run | Whether to execute this step | "Y" or "N" | Y means execute, N means skip |

### 5.4 TestData Sheet:
| Column Name | Description | Possible Values | Logic |
|-------------|-------------|-----------------|-------|
| Case ID | Corresponding test case ID | String | Must match Case ID in TestCases |
| Data Set | Data set identifier | String | Used to distinguish multiple sets of test data |
| Parameter Name | Parameter name | String | Corresponds to parameters in TestSteps |
| Value | Parameter value | Any type | Actual test data |
| Data Type | Data type | string, integer, json, etc. | Specifies the data type of the parameter |

### 5.5 Locators Sheet:
| Column Name | Description | Possible Values | Logic |
|-------------|-------------|-----------------|-------|
| Page | Page name | String | Corresponds to pages in PageModules |
| Element Name | Element name | String | Unique identifier |
| Locator Type | Location method | id, name, xpath, css, etc. | Selenium-supported location methods |
| Locator Value | Location value | String | Specific location expression |

### 5.6 PageModules Sheet:
| Column Name | Description | Possible Values | Logic |
|-------------|-------------|-----------------|-------|
| Page Name | Page name | String | Unique identifier |
| Module Name | Module name | String | Functional module within the page |
| Element Name | Element name | String | Corresponds to Element Name in Locators |
| Actions | Action name | String | E.g., click, input, verify, etc. |
| Parameter Name | Parameters | Comma-separated string | Parameters needed for the action |
| Highlight | Whether to highlight the element | "Y" or "N" | Y means highlight, N means don't highlight |
| Screenshot | Whether to take a screenshot | "Y" or "N" | Y means take screenshot, N means don't |
| Wait | Wait time after action (in seconds) | Number | Pause execution for specified time |
| Run | Whether to execute this action | "Y" or "N" | Y means execute, N means skip |

### 5.7 WebEnvironments Sheet:
| Column Name | Description | Possible Values | Logic |
|-------------|-------------|-----------------|-------|
| Environment | Environment name | DEV, SIT, UAT, PROD, etc. | Corresponds to active_environment in config file |
| URL | Environment URL | Complete URL string | Base URL of the test environment |
| Browser | Browser type | chrome, firefox, edge, etc. | Specifies the browser to use |

### 5.8 CustomActions Sheet:
| Column Name   | Description              | Possible Values | Logic |
|---------------|--------------------------|-----------------|-------|
| Action Name   | Custom action name       | String | Unique identifier |
| CustomAction1 | CustomAction python code | String | Custom python to be executed |

## 6. Writing Test Cases

### 6.1 API Test Cases

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

### 6.2 Web UI Test Cases

1. Fill in the TestCases sheet with test case details.
2. Define test steps in the TestSteps sheet.
3. Provide test data in the TestData sheet.
4. Define element locators in the Locators sheet.
5. Create page objects and modules in the PageModules sheet.
6. Configure environments in the WebEnvironments sheet.
7. Define custom actions in the CustomActions sheet if needed.

## 7. Running Tests

### 7.1 API Tests
```bash
python main.py --api
```

### 7.2 Web UI Tests
```bash
python main.py --web
```

### 7.3 E2E Tests
```bash
python main.py --e2e
```

### 7.4 Running Specific Test Cases or Tags

You can specify test case IDs or tags in the respective configuration files (api_test_config.yaml, web_test_config.yaml, e2e_test_config.yaml) to run specific tests.

## 8. Viewing Results

- Test results are generated in the `report` folder.
- Open `report.html` for a detailed test report.
- Check `log.html` for step-by-step execution logs.
- Screenshots for Web UI tests are embedded in the logs.
- A custom dashboard (dashboard.html) is generated with test statistics and charts.

## 9. Best Practices

1. Use meaningful test case IDs and names.
2. Leverage tags for easy filtering and organization.
3. Maintain clear and concise test step descriptions.
4. Regularly update and maintain test data.
5. Keep locators and page objects up-to-date with the application.
6. Use parameterization to create data-driven tests.
7. Implement proper error handling and logging in test scripts.
8. Regularly review and optimize test suites for efficiency.
9. Use the 'sanity check' tag for critical tests that, if failed, should prevent further testing.
10. Order your test cases so that sanity checks run first, followed by other tests.

## 10. Troubleshooting

- Check log files for detailed error messages.
- Verify configuration files for correct settings.
- Ensure all required dependencies are installed.
- Validate Excel file structure and content.
- Check for proper WebDriver setup for Web UI tests.
- If you encounter "ModuleNotFoundError", ensure you've installed all required packages (see Section 2.2).

## 11. Advanced Features

### 11.1 Dynamic Values in API Tests

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

### 11.2 Custom Python Actions in Web UI Tests

You can define custom Python actions in the CustomActions sheet of the Web UI test cases Excel file. These actions can be called from your test steps to perform complex operations or validations.

### 11.3 Sanity Check Implementation

The framework now supports a 'sanity check' feature:

- Tests tagged with 'sanity check' (case-insensitive) are treated as critical tests.
- If a sanity check test fails, all subsequent tests in the suite will be automatically skipped.
- This feature helps to quickly identify fundamental issues and saves time by not running further tests when basic functionality fails.

To use this feature:
1. Add the tag 'sanity check' to critical test cases in your Excel file.
2. Run your test suite as usual.
3. If a sanity check fails, you'll see skip messages for subsequent tests in the logs.

Example log output when a sanity check fails:
```
FAIL: Sanity Check Test
SKIP: Subsequent Test 1 - Skip current test TC002 due to Sanity Check failure
SKIP: Subsequent Test 2 - Skip current test TC003 due to Sanity Check failure
```

This feature is automatically enabled and requires no additional configuration beyond tagging your tests appropriately.

## 12. Maintenance and Updates

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
