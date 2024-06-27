# API Test Framework

This repository contains an API testing framework built in Python, aimed at automating the verification of API endpoints.

## Overview

The API Test Framework is designed to facilitate automated testing of various API endpoints by defining test cases in a systematic and configurable manner. The framework leverages Python's robustness and simplicity to define, execute, and log API tests. Key features include:

- **Environment Configuration:** Easily switch between different test environments (DEV, SIT, UAT) to ensure flexibility and comprehensive testing coverage.
- **Request and Response Handling:** Define default request bodies, templates, and headers to streamline test case creation and ensure consistency.
- **Dynamic Value Generation:** Automatically generate and inject dynamic values into test cases, such as user IDs, tokens, and other placeholder values.
- **Logging and Reporting:** Detailed logging of API requests and responses, along with the ability to save and reuse response fields in subsequent tests.
- **Excel Integration:** Use Excel files to define test cases, making it easy to manage and modify tests without altering the codebase.

## Getting Started

### Prerequisites

- Python 3.8 or higher
- Pip (Python package installer)

### Setup

1. Clone the repository:

    ```sh
    git clone <repository-url>
    cd <repository-name>
    ```

2. Install the dependencies:

    ```sh
    pip install -r requirements.txt
    ```

### Running Tests

To execute the tests, run the main script:

```sh
python api_main.py
```

This will run the test suite based on the configurations provided in `configs/test_config.yaml`.

## Configuration

### `configs/config.yaml`

Defines the active environment and available endpoints for different environments.

```yaml
active_environment: DEV

environments:
  DEV:
    endpoints:
      pacs.008_inbound:
        path: "http://localhost:5000/api/inbound_payment_json"
        method: "POST"
  # Additional environments...
```

### `configs/saved_fields.yaml`

Stores field values from previous test cases that can be reused in subsequent tests.

```yaml
PRE_001_01.response[3].balance: 57800.0
TC001_01.response.amount: 100
# Additional saved fields...
```

### `configs/test_config.yaml`

Specifies the path to the test cases, test case IDs to run, tags for filtering, and log level.

```yaml
test_cases_path: 'test_cases/web_test_cases.xlsx'
tc_id_list:
  - 'TC001'
tags:
  - 'tag1'
log_level: 'DEBUG'
```

### `configs/body_defaults`

Contains default JSON files for request bodies.

- `create_customer.json`
- `create_user.json`
- `pacs.008_in_def.json`
- `pacs.008_out_def.json`

### `configs/body_templates`

Includes the Jinja2 template files for request bodies.

- `pacs.008_in.json`
- `pacs.008_out.xml`
- `sample_create_customer.xml`
- `sample_create_user.json`

### `configs/headers`

Contains JSON files for request headers.

- `default.json`
- `default2.json`

## Creating Test Cases

Test cases should be defined in an Excel file specified by `test_cases_path` in `test_config.yaml`. Each test case should include the following columns:

| Column               | Description                                                                           |
| -------------------- | ------------------------------------------------------------------------------------- |
| **TCID**             | A unique identifier for a test case. Multiple test steps (TSID) can be associated with a single test case.                                                                       |
| **TSID**             | A unique identifier for a test step. A test case may consist of multiple test steps.                                                                          |
| **Descriptions**     | A brief description of the test step, explaining its specific function and testing purpose.                                                         |
| **Conditions**       | Conditions to check before running the test. Can include multiple lines and support   pre-conditions and post-conditions like `[suite setup]+tcid`, `[suite teardown]+tcid`, `[test setup]+tcid`, `[test teardown]+tcid`.                                       |
| **Endpoint**         | API endpoint to which the request should be sent.                                     |
| **Headers**          | Headers file to use. You can specify the header filename, and the header can also include variable placeholders set dynamically through `VariableGenerator`.           |
| **Template**         | The name of the request body template, pointing to predefined JSON or XML template files stored in the configuration file, rendered using Jinja2.                            |
| **Defaults**         | Default values file for the request body. These values support dynamic generation via `VariableGenerator`.                                                                 |
| **Body Modifications** | JSON string specifying any modifications to the request body. Use this to customize the body content, only setting the necessary fields that differ from the default values. Supports `${TC001_01.response.amount}` to dynamically use values from previous responses.                                                                         |
| **Run**              | Whether to run this test step (`'Y'` or `'N'`).                                       |
| **Tags**             | Tags associated with this test case. Tags help in filtering test cases to run specific sets defined in `test_config.yaml`.                                                  |
| **Exp Status**       | Expected HTTP status code.                                                            |
| **Exp Result**       | Expected result in the response body, can refer to fields from previous responses using `${TC001_01.response.amount}`.                                                 |
| **Save Fields**      | Fields from the response to save for later use.                                       |
| **Act Status**       | Actual HTTP status code (filled in by the framework).                                 |
| **Act Result**       | Actual result in the response body (filled in by the framework).                      |
| **Result**           | Test result (`'PASS'` or `'FAIL'`, filled in by the framework).                       |
| **Saved Fields**     | Fields saved from the response (filled in by the framework).                          |
| **API Timing**       | API execution time.                                                                   |

For example, a sample Excel test case might look like this:

| TCID  | TSID        | Descriptions | Conditions        | Endpoint          | Headers | Template    | Defaults      | Body Modifications                  | Run | Tags | Exp Status | Exp Result                     | Save Fields            | Act Status | Act Result               | Result | Saved Fields            | API Timing |
|-------|-------------|--------------|-------------------|-------------------|---------|-------------|---------------|-------------------------------------|-----|------|------------|--------------------------------|-------------------------|------------|-------------------------|--------|-------------------------|------------|
| PRE_001 | PRE_001_01  |              |                   | positions         | default |             |               |                                     | Y   | tag1 | 200        | response[3].balance=57800.0   | response[3].balance     | 200        | response[3].balance:PASS | PASS   | response[3].balance=57800.0 | 2.05s      |
| PRE_001 | PRE_001_02  |              |                   | positions         | default |             |               |                                     | Y   | tag1 | 200        | response[3].balance=57800.0   | response[3].balance     | 200        | response[3].balance:PASS | PASS   | response[3].balance=57800.0 | 2.06s      |
| TC001   | TC001_01    |              | [test setup]PRE_001 | pacs.008_inbound  | default | pacs.008_in | pacs.008_in_def | {"amount": 100}                    | Y   | tag1 | 200        | response.amount=100           | response.amount         | 200        | response.amount:PASS     | PASS   | response.amount=100       | 2.05s      |
| TC001   | TC001_02    |              |                   | pacs.008_outbound | default | pacs.008_out | pacs.008_out_def | {"amount": ${TC001_01.response.amount}} | Y   | tag1 | 200        | response.amount=${TC001_01.response.amount} | response.amount         | 200        | response.amount:FAIL     | FAIL   | response.amount=100.0     | 2.06s      |

## Log Files

Log files are generated in the `log` directory. The log level can be configured in `test_config.yaml`. Each log entry includes timestamps, log level, and a message describing the logged event.

```plaintext
log/
├── log_YYYY-MM-DD_HH-MM-SS.log
```

These log files provide detailed trace information regarding the test execution, including requests, responses, and any errors encountered.
