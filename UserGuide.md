# Guidelines for Filling the Test Suite

## 1.Conditions Column

The **Conditions** column is used to define the prerequisites that need to be met before running a particular test step. These conditions can include both setup and teardown requirements and support multiline entries. The conditions are parsed and executed by the code before the actual test execution.

### 1. Support for Multiple Conditions
- **Multiline Entries**: Each condition should be written on a separate line to support multiple conditions.

### 2. Setup Conditions
- **Suite Setup**: Use `[suite setup]` to specify conditions that need to be met before running the entire test suite.
- **Test Setup**: Use `[test setup]` to specify conditions that need to be met before running an individual test case.

### 3. Teardown Conditions
- **Suite Teardown**: Use `[suite teardown]` to specify conditions that need to be met after running the entire test suite.
- **Test Teardown**: Use `[test teardown]` to specify conditions that need to be met after running an individual test case.

### 4. Associating Test Cases
- **Link Test Cases**: After specifying `[suite setup]`, `[test setup]`, `[suite teardown]`, or `[test teardown]`, append the ID of the test case that needs to be executed for that condition.

### Example Entries:
```plaintext
[suite setup]PRE_001
[test setup]INIT_001
```

In this example:
- `[suite setup]PRE_001`: Indicates that the `PRE_001` test case should be executed as a suite-level setup condition before running all test cases.
- `[test setup]INIT_001`: Indicates that the `INIT_001` test case should be executed as a test-level setup condition before running the specific test step.

### Summary:
- **Multiline Conditions**: Write each condition on a separate line.
- **Setup Conditions**: Use `[suite setup]` or `[test setup]` for prerequisites before running tests.
- **Teardown Conditions**: Use `[suite teardown]` or `[test teardown]` for prerequisites after running tests.
- **Link Test Cases**: Associate the condition with a specific test case ID.

By following these guidelines, you can ensure that all necessary conditions are clearly defined and correctly executed before and after your test steps, thereby maintaining the integrity and reliability of your test suite.



## 2.Endpoint Column

The **Endpoint** column is used to specify the API endpoint to which the request will be sent. This endpoint is defined in the configuration file (`config.yaml`). During the execution of a test step, the test framework will look up the corresponding endpoint information based on the value provided in the Endpoint column.

### 1. Matching with Configuration File
- **Consistent Naming**: The value entered in the Endpoint column must match the endpoint name defined in the `config.yaml` configuration file. Consistency in naming ensures that the correct endpoint information is retrieved during test execution.

### 2. Endpoint Path and Method
- **Configuration Specifics**: The actual path and HTTP method for the endpoint are specified in the `config.yaml` file. There is no need to specify the endpoint path and HTTP method in the Excel sheet; they will be automatically retrieved from the configuration file during test execution.

### 3. Adaptation to Different Environments
- **Environment Flexibility**: A single endpoint name can be used to adapt to different API server addresses in various testing environments (e.g., DEV, SIT, UAT). This allows for seamless switching between environments without modifying the test cases.

### Example Configuration (`config.yaml`):
```yaml
environments:
  DEV:
    endpoints:
      create_user:
        path: "http://localhost:5000/api/create_user"
        method: "POST"
  SIT:
    endpoints:
      create_user:
        path: "https://sit.example.com/api/create_user"
        method: "POST"
  UAT:
    endpoints:
      create_user:
        path: "https://uat.example.com/api/create_user"
        method: "POST"
        
```

#### Example Entry in Endpoint Column:
```plaintext
create_user
```

In this example:
- **`create_user`**: The value in the Endpoint column should match the endpoint name (`create_user`) defined in the `config.yaml` file. The test framework will look up the corresponding path and method based on the active environment.

### Summary:
- **Consistent Naming**: Ensure the value matches an endpoint name in `config.yaml`.
- **Configuration Specifics**: Path and method are defined in `config.yaml`, not in the Excel sheet.
- **Environment Flexibility**: Use the same endpoint name across different environments for consistency.

By following these guidelines, you can ensure that the correct endpoint information is retrieved and used during test execution, facilitating accurate and efficient testing of your API endpoints.





## 3.Headers Column

The **Headers** column is used to specify the filename of the JSON file that contains the request headers information. These files are stored in the `configs/headers` directory. The content of the files indicated in the Headers column will be loaded before sending the request and can include dynamically generated or populated variable values.

### 1. Filename Specification
- **Filename Only**: Enter the name of the JSON file without including the file extension (.json). For example, for a file named `default.json`, simply enter `default` in the Headers column.
- **Directory**: Ensure that the file is located in the `configs/headers` directory for it to be correctly identified and loaded.

### 2. Variable Placeholders
- **Placeholders**: Request header files can include variable placeholders (e.g., `{{ token }}`). These placeholders will be replaced with actual values before the request is sent.

### 3. Dynamic Value Generation
- **Dynamic Values**: Use the `VariableGenerator` class to dynamically generate certain values in the request headers, such as `token`. This allows for automated and context-specific value generation.

### 4. Loading and Processing
- **Pre-Request Processing**: The framework will load and process the request header file before sending the request, ensuring all placeholders are replaced with actual values.

### Example JSON File Content (`default.json`):
```json
{
  "Content-Type": "application/json",
  "accept": "application/json",
  "Authorization": "{{ token }}",
  "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.93 Safari/537.36"
}
```

### Example Entry in Headers Column:
```plaintext
default
```

In this example:
- The `Authorization` header in the `default.json` file contains a placeholder `{{ token }}`, which will be dynamically replaced with an actual token value before the request is sent.

### Summary:
- **Filename**: Enter the base filename without extension.
- **Directory**: Files should be located in `configs/headers`.
- **Placeholders**: Use placeholders for values that need to be dynamically replaced.
- **Dynamic Values**: Utilize the `VariableGenerator` class to generate dynamic header values.
- **Pre-Request Processing**: Framework ensures all placeholders are replaced with actual values before sending requests.

By following these guidelines, you can ensure that the correct request headers are used during test execution, facilitating precise and flexible API testing.





## 4.Template Column

The **Template** column is used to specify the filename of the request body template. These templates are stored in the `configs/body_templates` directory and are in Jinja2 format. During the request generation process, the template files are loaded and rendered using the Jinja2 template engine, combining default values and modification values to generate the final request body.

### 1. Filename Specification
- **Filename Only**: Enter the name of the template file without including the file extension. For example, for a file named `pacs.008_in.json`, simply enter `pacs.008_in` in the Template column.
- **Directory**: Ensure that the file is located in the `configs/body_templates` directory for it to be correctly identified and loaded.

### 2. Supported Formats
- **JSON or XML**: Template files can be in either JSON or XML format, allowing for flexibility in defining the request body structure.

### 3. Jinja2 Rendering
- **Template Engine**: The Jinja2 template engine is used to render the template files. This allows for the inclusion of placeholders in the form of `{{ variable_name }}`, which will be replaced with actual values during the rendering process.

### 4. Support for Loops and Conditions
- **Dynamic Content**: Jinja2 supports the use of loops and conditional statements within the template files. This enables the creation of complex, dynamic request bodies based on varying conditions.

### 5. Merging Default and Modification Values
- **Combining Values**: During the request body generation, the content from the defaults file and the Body Modifications column are merged into the template. This ensures that the final request body is comprehensive and accurate.

### Example Template File Content (`pacs.008_in.json`):
```json
{
  "transaction_id": "{{ transaction_id }}",
  "amount": {{ amount }},
  "currency": "{{ currency }}",
  "debtor": {
    "name": "{{ debtor.name }}",
    "phones": [
      {% for phone in debtor.phones %}
      "{{ phone }}"
      {% if not loop.last %},{% endif %}
      {% endfor %}
    ],
    "email": "{{ debtor.email }}",
    "address": "{{ debtor.address }}"
  },
  "creditor": {
    "name": "{{ creditor.name }}",
    "phones": [
      {% for phone in creditor.phones %}
      "{{ phone }}"
      {% if not loop.last %},{% endif %}
      {% endfor %}
    ],
    "email": "{{ creditor.email }}",
    "address": "{{ creditor.address }}"
  }
}
```

### Example Entry in Template Column:
```plaintext
pacs.008_in
```

In this example:
- The template file `pacs.008_in.json` contains placeholders and loops that will be dynamically replaced and iterated over during the rendering process.

### Summary:
- **Filename**: Enter the base filename without extension.
- **Directory**: Files should be located in `configs/body_templates`.
- **Supported Formats**: Templates can be in JSON or XML format.
- **Dynamic Rendering**: Use Jinja2 placeholders (`{{ variable_name }}`) for dynamic content.
- **Loops and Conditions**: Utilize Jinja2 loops and conditional statements for complex templates.
- **Value Merging**: Combine defaults and Body Modifications content into the final template.

By following these guidelines, you can ensure that the request body templates are correctly specified and dynamically rendered, allowing for flexible and accurate API request testing.




## 5.Defaults Column

The **Defaults** column specifies the filename of the JSON file that contains the default request body data. These files are stored in the `configs/body_defaults` directory. The content of the files indicated in the Defaults column will be loaded and dynamically supplemented as per the following rules:

### 1. Filename Specification
- **Filename Only**: Enter the name of the JSON file without including the file extension (.json). For example, for a file named `create_user.json`, simply enter `create_user` in the Defaults column.
- **Directory**: Ensure that the file is located in the `configs/body_defaults` directory for it to be correctly identified and loaded.

### 2. Structure Generation
- **Base Structure**: The content of the specified JSON file will serve as the base structure for generating the request body. This ensures a consistent starting point for constructing the request payload.

### 3. Dynamic Values
- **Variable Support**: The JSON files support dynamic values generated by the `VariableGenerator` class. You can include template engine markers within the JSON file to denote these dynamic values. For example, you can use `{{ phones.number }}` to indicate a placeholder for a dynamically generated phone number.
- **Automatic Replacement**: During the request body generation, these placeholders will be automatically identified and replaced with the corresponding dynamic values.

### 4. Overrides
- **Body Modifications**: Any values specified in the **Body Modifications** column will override the corresponding values in the default JSON file. This allows for flexible and specific adjustments to the request payload based on the needs of individual test cases.

### Example JSON File Content (`create_user.json`):
```json
{
  "name": "John Doe",
  "email": "john.doe@example.com",
  "address": {
    "street": "123 Main St",
    "city": "Anytown",
    "state": "CA",
    "zip": "{{ address.zip }}"
  },
  "phones": [
    {
      "type": "home",
      "number": "555-555-5555"
    },
    {
      "type": "work",
      "number": "{{ phones.number }}"
    }
  ],
  "preferences": {
    "newsletter": true,
    "notifications": {
      "email": true,
      "sms": false
    }
  }
}
```
In this example, the `address.zip` and `phones.number` fields will be dynamically generated and replaced at runtime.

### Summary
- **Filename**: Enter the base filename without extension.
- **Directory**: Files should be located in `configs/body_defaults`.
- **Dynamic Values**: Use placeholders for dynamic values.
- **Overrides**: Use the **Body Modifications** column to override defaults.

By following these guidelines, you can effectively leverage the Defaults column to streamline and standardize your request body generation process.




## 6.Body Modifications Column

The **Body Modifications** column is used to specify the values for specific fields in the request body that need to be modified. These values will override the corresponding fields in the default values file and template file to generate the final request body. The contents of the Body Modifications column must be in valid JSON format.

### 1. JSON Format
- **Valid JSON**: The content entered in this column must be in valid JSON format. This ensures that the values can be correctly parsed and applied to the request body.

### 2. Field Overrides
- **Overwrite Fields**: Fields specified in the JSON object will override the corresponding fields in the default values file and template file. This allows for precise control over the values used in the final request body.

### 3. Dynamic Values
- **Dynamic Content**: Supports the use of `${TCID.response.field}` syntax to retrieve dynamic values from previous responses. This allows for the incorporation of context-specific data into the request body.

### 4. Nested Structures
- **Nested Fields**: Supports nested structures for field overrides. You can recursively specify modification values for nested fields, ensuring comprehensive control over complex request bodies.

### Example Entry in Body Modifications Column:
```json
{
  "amount": 2000,
  "debtor": {
    "name": "Bruce Wayne",
    "email": "bruce.wayne@example.com"
  },
  "creditor": {
    "name": "Clark Kent",
    "phones": [
      "555-123-4567",
      "${TC001.response.creditor.phone}"
    ]
  }
}
```

In this example:
- The `amount` field is overridden to be `2000`.
- The `debtor` object is modified with new `name` and `email` values.
- The `creditor` object is modified with a new `name` and an array for `phones`, where the second phone number is dynamically retrieved from the response of a previous test case identified by `TC001`.

### Summary:
- **Valid JSON**: Ensure the content is in valid JSON format.
- **Overwrite Fields**: Fields in the JSON object will override corresponding fields in defaults and templates.
- **Dynamic Values**: Use `${TCID.response.field}` to fetch dynamic values from previous responses.
- **Nested Structures**: Support modifications for nested fields.

By following these guidelines, you can effectively utilize the Body Modifications column to customize the request body as needed for accurate and flexible API testing.



## 7.Tags Column

The **Tags** column is used to categorize and filter test cases. You can specify which tags of test cases to run in the test configuration file, allowing for flexible selection and filtering of test cases.

### 1. Comma-Separated Values
- **Multiple Tags**: When specifying multiple tags, use a comma to separate them. This allows for the assignment of multiple categories to a test case.

### 2. Flexible Categorization
- **Custom Tags**: Tags can be freely defined based on your needs. Examples include `tag1`, `tag2`, `critical`, `regression`, etc. This flexibility supports a wide range of categorization criteria.

### 3. Configuration Filtering
- **Specified Tags**: In the configuration file (`test_config.yaml`), specify the tags to run using the `tags` list. Only test cases that contain these tags will be executed. This method facilitates targeted testing based on specific criteria.

### 4. Case Insensitivity
- **Case-Insensitive Matching**: Tag matching is case-insensitive. This means `Tag1` and `tag1` will be considered equivalent, ensuring consistency irrespective of case variations.

### 5. Combining Tags
- **Complex Filtering**: By combining multiple tags, you can implement more complex test case filtering logic. This combination allows for highly specific selections based on intersecting categories.

### Example Configuration (`test_config.yaml`):
```yaml
tags:
  - tag1
  - critical
```

### Example Entry in Tags Column:
```plaintext
tag1, critical
```

In this example:
- The test case is assigned the `tag1` and `critical` tags.
- When the configuration file specifies `tag1` and `critical` in the tags list, this test case will be executed.

### Summary:
- **Multiple Tags**: Use commas to separate multiple tags.
- **Custom Tags**: Define tags as needed for flexible categorization.
- **Specified Tags**: Use the `tags` list in the configuration file to specify which tags to run.
- **Case-Insensitive**: Tag matching ignores case differences.
- **Combined Tags**: Combine multiple tags for complex test case filtering.

By following these guidelines, you can efficiently categorize and filter your test cases using the Tags column, enhancing the flexibility and specificity of your test suite execution.




## 8.Run Column

The **Run** column is used to indicate whether a particular test step in a test case should be executed. The value can be 'Y' or 'N', representing `execute` and `do not execute`, respectively.

### 1. **Y or N Values**
- **Accepted Values**: The value entered must be either 'Y' or 'N'. The case of the letters does not matter, so 'y' and 'n' are also acceptable.
- **Execution Directive**: 'Y' indicates that the test step should be executed, whereas 'N' indicates that it should not be executed.

### 2. Execution Logic
- **Filtering Mechanism**: Before executing the test suite, the framework will filter out the test steps that do not need to be executed based on the value in the Run column.

### 3. Logical Summary
- **Initial Filtering**: After loading the test case file, the framework will first filter out test steps that should not be executed based on the Run column value.
   - **Run = 'Y'**: The test step will be considered for execution.
   - **Run = 'N'**: The test step will be excluded from execution.
- **Additional Filtering**: Further filtering will be performed based on the tags and `tc_id_list` specified in the configuration file.
- **Final Execution**: Finally, the framework will execute only those test steps where the Run column value is 'Y' and that meet the tag and ID filtering criteria.

### Example Entry in Run Column:
```plaintext
Y
```
or
```plaintext
N
```

In this example:
- **'Y'**: Indicates that the corresponding test step should be executed.
- **'N'**: Indicates that the corresponding test step should not be executed.

### Summary:
- **Accepted Values**: 'Y' or 'N' (case-insensitive).
- **Execution Directive**: 'Y' to execute the test step, 'N' to skip it.
- **Initial Filtering**: Framework filters based on the Run column before considering tags and IDs.
- **Additional Filtering**: Further filters are applied based on tags and `tc_id_list` in the configuration file.
- **Final Execution**: Only steps marked 'Y' and matching other filters are executed.

By following these guidelines, you can clearly indicate which test steps should be executed, ensuring an efficient and targeted test suite execution.



## 9.Exp Status (Expected Status) Column

The **Exp Status** (Expected Status) column is used to specify the expected HTTP status code for a test step. This status code indicates the HTTP response code that the server is expected to return after the request is sent. The framework will validate this status code during the execution of the test step.

### 1. HTTP Status Codes
- **Valid HTTP Codes**: The value entered must be a valid HTTP status code, such as `200`, `201`, `404`, `500`, etc.

### 2. Integer Representation
- **Integer Format**: Status codes should be represented as integers to indicate the expected return status.

### 3. Comparison Logic
- **Validation**: The framework will compare the actual response status code with the expected status code specified in this column. If they do not match, the test step will be marked as failed.

### 4. Mandatory Field
- **Required for Validation**: This field must be filled if you intend to validate the HTTP status code. It ensures that the framework can correctly perform the comparison.

### Example Status Codes:
- **200**: OK - Request was successful.
- **201**: Created - Resource was successfully created.
- **400**: Bad Request - The request could not be understood or was missing required parameters.
- **401**: Unauthorized - Authentication failed or user does not have permissions for the desired action.
- **404**: Not Found - Resource was not found.
- **500**: Internal Server Error - An error occurred on the server.

### Example Entry in Exp Status Column:
```plaintext
200
```
or
```plaintext
404
```

In this example:
- **`200`**: Indicates that the expected HTTP status code for the test step is `200` (OK).
- **`404`**: Indicates that the expected HTTP status code for the test step is `404` (Not Found).

### Summary:
- **Valid HTTP Codes**: Ensure the value is a valid HTTP status code.
- **Integer Format**: Status codes should be in integer format.
- **Validation**: The framework will compare the actual response code with the expected code.
- **Mandatory Field**: This field must be filled if the status code is to be validated.

By following these guidelines, you can correctly specify the expected HTTP status codes for your test steps, ensuring accurate validation of API responses.







## 10.Exp Result (Expected Result) Column

The **Exp Result** (Expected Result) column is used to specify the expected response content for a test step. This helps in verifying whether the response returned by the server meets the expectations.

### 1. Key-Value Pair Format
- **Format**: Each line should contain one expected result in the format of `field_path=expected_value`.

### 2. Field Path
- **Dot Notation**: Use dot notation to represent properties of a JSON object, and support array indexing (e.g., `response.items[0].id`).

### 3. Expected Values
- **Data Types**: The expected value can be a string, number, boolean, etc. It also supports dynamic values from previous responses (e.g., `${TCID.response.field}`).
- **Strings**: String values should be enclosed in double quotes, e.g., `response.status="success"`.
- **Numbers and Booleans**: Values can be written without quotes, e.g., `response.code=200` or `response.valid=true`.

### 4. Multiple Lines Support
- **Newline Separation**: Use newline characters to separate different expected results. Each expected result should be on a separate line.

### 5. Whitespace and Quotes
- **Whitespace Handling**: Leading and trailing spaces around the key-value pairs are trimmed.
- **Quotes for Strings**: String values must be enclosed in double quotes. Non-quoted parts are automatically treated as numbers or booleans.

### Example Entries in Exp Result Column:
```plaintext
response.status="success"
response.code=200
response.items[0].id="12345"
response.valid=true
response.amount=${TC001.response.amount}
```
In this example:
- **`response.status="success"`**: Expected value for `status` is `"success"`.
- **`response.code=200`**: Expected value for `code` is `200`.
- **`response.items[0].id="12345"`**: Expected value for `id` in the first item of `items` array is `"12345"`.
- **`response.valid=true`**: Expected value for `valid` is `true`.
- **`response.amount=${TC001.response.amount}`**: Expected value for `amount` is dynamically taken from the response of a previous test case identified by `TC001`.

### Summary:
- **Key-Value Pair Format**: Use `field_path=expected_value` format.
- **Dot Notation**: Represent JSON object properties and arrays using dot notation.
- **Data Types**: Expected values can be strings, numbers, booleans, or dynamic values.
- **Multiple Lines**: Use newlines to separate different expected results.
- **Quotes for Strings**: Enclose string values in double quotes.

By following these guidelines, you can clearly specify the expected response content for your test steps, ensuring accurate validation of API responses.



## 11.Save Fields (Save Fields) Column

The **Save Fields** column is used to specify the fields that should be saved from the response of a test step. These saved fields can be referenced and used in subsequent test steps.

### 1. Path Format
- **Field Paths**: Each entry should use the field path (e.g., `response.field`) to specify the field to be saved. Multiple fields can be specified on separate lines.

### 2. Nested Support
- **Nested Objects**: Field paths can include nested objects (e.g., `response.user.name`) and array indices (e.g., `response.items[0].id`). This allows for precise selection of specific data within the response.

### 3. Dynamic References
- **Reference in Subsequent Steps**: The saved fields can be referenced in subsequent test steps or cases using variable syntax (e.g., `${TC001_01.response.amount}`). This enables dynamic and context-aware testing.

### 4. Data Persistence
- **Persistent Storage**: The values of saved fields are persisted to a file, ensuring they are available for use in later test steps. This persistence mechanism ensures data consistency across multiple test cases.

### Example Entries in Save Fields Column:
```plaintext
response.amount
response.user.name
response.items[0].id
response.status
```

In this example:
- **`response.amount`**: The value of the `amount` field in the response will be saved.
- **`response.user.name`**: The value of the `name` field within the `user` object in the response will be saved.
- **`response.items[0].id`**: The value of the `id` field in the first item of the `items` array in the response will be saved.
- **`response.status`**: The value of the `status` field in the response will be saved.

### Summary:
- **Field Paths**: Specify using `field_path` format for individual fields.
- **Nested Objects**: Include nested objects and array indices in field paths.
- **Dynamic References**: Use saved fields in later steps with `${TCID.response.field}` syntax.
- **Persistent Storage**: Saved field values are stored for future use.

By following these guidelines, you can accurately specify which fields to save from the response, enabling dynamic and context-aware testing in subsequent steps.




## 12.Act Status, Act Result, Result, Saved Fields, and API Timing Columns

### Act Status Column
- **Purpose**: Records the actual HTTP status code.
- **Data Source**: This column is automatically populated by the framework with the HTTP response status code returned by the server after executing the test step.

### Act Result Column
- **Purpose**: Records the actual response content.
- **Data Source**: This column is automatically populated by the framework with the actual response data returned by the server after executing the test step.

### Result Column
- **Purpose**: Records the outcome of the test step, indicating whether it is `PASS` or `FAIL`.
- **Data Source**: This column is automatically populated by the framework after comparing the expected and actual results.

### Saved Fields Column
- **Purpose**: Records the saved fields and their values.
- **Data Source**: This column is automatically populated by the framework with the fields specified in the Save Fields column and their corresponding values after the response has been processed.

### API Timing Column
- **Purpose**: Records the execution time of the API call.
- **Data Source**: This column is automatically populated by the framework with the time taken to execute the API call after the test step is completed.

### Example Entries (Automatically Filled by the Framework):
```plaintext
Act Status:
200

Act Result:
{
  "status": "success",
  "data": {
    "id": "12345",
    "name": "example"
  }
}

Result:
PASS

Saved Fields:
response.data.id="12345"
response.status="success"

API Timing:
2.34s
```

### Summary:
- **Act Status**: Automatically records the actual HTTP status code returned by the server.
- **Act Result**: Automatically records the actual response body returned by the server.
- **Result**: Automatically records the test step's result as `PASS` or `FAIL` based on the comparison between expected and actual results.
- **Saved Fields**: Automatically records the fields specified in the Save Fields column and their actual values from the response.
- **API Timing**: Automatically records the execution time of the API call.

These columns are automatically managed by the framework to provide an accurate record of each test step's execution and results.
