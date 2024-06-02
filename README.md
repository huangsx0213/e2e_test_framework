# API Testing Framework Requirements Specification

## Introduction

This document provides a detailed requirements specification for an API testing framework. The framework aims to streamline and automate the testing of API endpoints, ensuring comprehensive test coverage, accurate results logging, and detailed reporting.

## Table of Contents

1. [Overview](#overview)
2. [Requirements](#requirements)
   - [Core Components](#core-components)
     - [TestCaseExecutor](#testcaseexecutor)
     - [Logger](#logger)
     - [RequestBodyBuilder](#requestbodybuilder)
     - [RequestHeadersBuilder](#requestheadersbuilder)
     - [RequestSender](#requestsender)
     - [ResponseHandler](#responsehandler)
     - [TemplateRenderer](#templaterenderer)
     - [VariableGenerator](#variablegenerator)
3. [Classes and Methods](#classes-and-methods)
   - [TestCaseExecutor](#testcaseexecutor-1)
   - [Logger](#logger-1)
   - [RequestBodyBuilder](#requestbodybuilder-1)
   - [RequestHeadersBuilder](#requestheadersbuilder-1)
   - [RequestSender](#requestsender-1)
   - [ResponseHandler](#responsehandler-1)
   - [TemplateRenderer](#templaterenderer-1)
   - [VariableGenerator](#variablegenerator-1)

## Overview

The API Testing Framework is designed to automate the process of testing RESTful APIs. It allows for the definition of test cases, preparation of request bodies and headers, sending requests, logging requests and responses, and handling responses. The framework supports templating for request bodies and headers, and it dynamically generates variable values for testing purposes.

## Requirements

### Core Components

#### TestCaseExecutor

- **Purpose**: Executes test cases defined in an Excel file.
- **Inputs**:
  - Path to the test cases Excel file.
- **Outputs**:
  - Logs of requests and responses.
  - Updated test cases file with test results.

#### Logger

- **Purpose**: Logs request and response details.
- **Inputs**:
  - Request and response data.
- **Outputs**:
  - Log files.

#### RequestBodyBuilder

- **Purpose**: Prepares request bodies using templates and default values.
- **Inputs**:
  - Template name.
  - Default values.
  - Modifications.
- **Outputs**:
  - Rendered request body.

#### RequestHeadersBuilder

- **Purpose**: Prepares request headers.
- **Inputs**:
  - Header modifications.
- **Outputs**:
  - Prepared headers.

#### RequestSender

- **Purpose**: Sends HTTP requests.
- **Inputs**:
  - Base URL.
  - HTTP method.
  - Endpoint.
  - Headers.
  - Body.
- **Outputs**:
  - HTTP response.

#### ResponseHandler

- **Purpose**: Handles API responses and updates test cases file.
- **Inputs**:
  - Response.
  - Test case data.
  - Path to the test cases file.
  - Row index of the test case.
- **Outputs**:
  - Logs.
  - Updated test cases file.

#### TemplateRenderer

- **Purpose**: Renders templates using Jinja2.
- **Inputs**:
  - Template name.
  - Context data.
- **Outputs**:
  - Rendered template content.

#### VariableGenerator

- **Purpose**: Generates dynamic values for request headers and bodies.
- **Inputs**: None.
- **Outputs**:
  - Dictionary of generated variables.

## Classes and Methods

### TestCaseExecutor

#### Methods

- `__init__(self, test_cases_path: str, logger: Logger, body_builder: RequestBodyBuilder, headers_builder: RequestHeadersBuilder, request_sender: RequestSender, response_handler: ResponseHandler) -> None`
  - Initializes the TestCaseExecutor with required components.

- `execute_test_cases(self) -> None`
  - Executes the test cases defined in the provided Excel file.

### Logger

#### Methods

- `__init__(self, log_dir: str) -> None`
  - Initializes the Logger with the log directory.

- `log_request(self, test_id: str, endpoint_name: str, method: str, endpoint: str, headers: dict, body: dict, format_type: str) -> str`
  - Logs the request details to a file and returns the log file path.

- `log_response(self, log_filepath: str, response: Response, format_type: str) -> None`
  - Logs the response details to the same file as the request.

### RequestBodyBuilder

#### Methods

- `__init__(self, template_dir: str, body_defaults: dict, templates: dict) -> None`
  - Initializes the RequestBodyBuilder with the template directory, default values, and templates.

- `prepare_body(self, template_name: str, default_values: dict, modifications: dict, format_type: str) -> str`
  - Prepares the request body by rendering the template with default values and modifications.

### RequestHeadersBuilder

#### Methods

- `__init__(self, headers_config: dict) -> None`
  - Initializes the RequestHeadersBuilder with the headers configuration.

- `prepare_headers(self, header_modifications: dict) -> dict`
  - Prepares the request headers by merging default headers and modifications.

### RequestSender

#### Methods

- `send_request(self, base_url: str, method: str, endpoint: str, headers: dict, body: dict, format_type: str) -> Response`
  - Sends an HTTP request and returns the response.

### ResponseHandler

#### Methods

- `__init__(self, logger: Logger) -> None`
  - Initializes the ResponseHandler with the Logger.

- `handle_response(self, response: Response, test_case: pd.Series, test_cases_path: str, row_idx: int) -> None`
  - Handles the API response by logging it and updating the test cases file with the result.

### TemplateRenderer

#### Methods

- `__init__(self, template_dir: str) -> None`
  - Initializes the TemplateRenderer with the template directory.

- `render_template(self, template_name: str, context: dict, format_type: str) -> str`
  - Renders a template with the given context.

### VariableGenerator

#### Methods

- `generate_variables(self) -> dict`
  - Generates a dictionary of dynamic variables.

- `generate_token(self, length: int = 16) -> str`
  - Generates a random token.

- `generate_random_string(self, length: int) -> str`
  - Generates a random string.

- `generate_phone_number(self) -> str`
  - Generates a random phone number.

- `generate_zipcode(self) -> str`
  - Generates a random ZIP code.