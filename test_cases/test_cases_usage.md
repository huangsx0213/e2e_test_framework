# Excel Filling Guide

This guide provides detailed instructions on how to fill out the test case Excel file. Each column represents a specific field used to define various aspects of the test cases and expected results.

## Header Definitions

| TCID | TSID | Descriptions | Preconditions | Endpoint | Headers | Template | Defaults | Body Modifications | Run | Tags | Exp Status | Exp Result | Save Fields | Act Status | Act Result | Result | Saved Fields |
|------|------|--------------|----------------|----------|---------|----------|----------|--------------------|-----|------|-------------|--------------|--------------|------------|------------|---------|----------------|
| TC001 | TC001_01 | | | pacs.008_inbound | default | pacs.008_in | pacs.008_in_def | {"amount": 100} | Y | tag1 | 200 | response.amount=100 | response.amount | 200 | response.amount:pass | pass | response.amount=100 |

## Column Definitions

- **TCID**: `Test Case ID` - A unique identifier for a test case. Multiple test steps (TSID) can be associated with a single test case.
- **TSID**: `Test Step ID` - A unique identifier for a test step. A test case may consist of multiple test steps.
- **Descriptions**: `Description` - A brief description of the test step, explaining its specific function and testing purpose.
- **Preconditions**: `Preconditions` - Conditions that must be met before executing the test step. Usually used to describe the required prior setup or state.
- **Endpoint**: `Endpoint` - The API endpoint name to be tested. Corresponds to the endpoint name in the configuration file.
- **Headers**: `Headers` - The name of the HTTP headers file, pointing to predefined HTTP headers stored in the configuration file.
- **Template**: `Template` - The name of the request body template, pointing to predefined JSON or XML template files stored in the configuration file.
- **Defaults**: `Defaults` - The name of the default values for the request body, pointing to predefined default value files stored in the configuration file.
- **Body Modifications**: `Body Modifications` - Fields and values used to modify the default request body. Defined using JSON format.
- **Run**: `Run` - Indicates whether to run this test step. Usually 'Y' denotes that this step should be executed.
- **Tags**: `Tags` - Tags used to classify and filter test cases. You can specify one or more tags.
- **Exp Status**: `Expected Status` - The expected HTTP response status code.
- **Exp Result**: `Expected Result` - The expected response results, defined using field paths and expected values. Each line denotes a comparison of one expected value.
- **Save Fields**: `Save Fields` - Response field values that need to be saved and passed to other test steps. Defined using field paths.
- **Act Status**: `Actual Status` - The actual HTTP response status code. Filled in by the test execution code.
- **Act Result**: `Actual Result` - The actual response result. Filled in by the test execution code.
- **Result**: `Result` - The final test result, usually 'pass' or 'fail'. Filled in by the test execution code.
- **Saved Fields**: `Saved Fields` - The actual saved fields and their values. Filled in by the test execution code.

## Additional Notes

- **Body Modifications and Exp Result**: You can dynamically modify parameters / Exp Result in the request body. For example, `{"amount": ${TC001_01.response.amount}}` refers to using the saved `amount` value from the previous test step.
  
- **Exp Result and Save Fields**: Expected results and fields to save support using path references (e.g., `response.amount`), which are used to parse and verify the response JSON structure.
  
- **Run**: Set to `Y` to run the test step; otherwise, the test step will be skipped.

## Usage Tips

- Ensure each test case (TCID) has a unique identifier.
- Each test step (TSID) should also have a unique identifier, but test steps can share the same test case ID (TCID).
- Use descriptive tags (Tags) to filter and run specific categories of test cases conveniently.
- During the actual test execution, use scripts or automation tools to populate the `Act Status`, `Act Result`, `Result`, and `Saved Fields` columns.

By following these guidelines, you can systematically organize and manage your test cases, ensuring their coverage and maintainability.
---

## Example Overview

Below is a simple example containing two test steps (TSID) that belong to the same test case (TCID).

```markdown
| TCID  | TSID       | Descriptions | Preconditions | Endpoint        | Headers | Template    | Defaults      | Body Modifications               | Run | Tags | Exp Status | Exp Result                                    | Save Fields                  | Act Status | Act Result                   | Result | Saved Fields              |
|-------|------------|--------------|---------------|-----------------|---------|-------------|---------------|----------------------------------|-----|------|------------|---------------------------------------------|------------------------------|------------|------------------------------|--------|----------------------------|
| TC001 | TC001_01   |              |               | pacs.008_inbound| default | pacs.008_in | pacs.008_in_def| {"amount": 100}                  | Y   | tag1 | 200        | response.amount=100                         | response.amount              | 200        | response.amount:pass         | pass   | response.amount=100        |
| TC001 | TC001_02   |              |               | pacs.008_outbound| default| pacs.008_out| pacs.008_out_def| {"amount": ${TC001_01.response.amount}} | Y   | tag1 | 200        | response.amount=${TC001_01.response.amount} | response.amount              | 200        | response.amount:fail         | fail   | response.amount=100.0      |