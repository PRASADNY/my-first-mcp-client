# Running Tests for MCP Client

This directory contains unit tests for the MCP Client.

## Installation

Install test dependencies:

```bash
pip install -e ".[test]"
```

Or using `uv`:

```bash
uv pip install -e ".[test]"
```

## Running Tests

Run all tests:

```bash
pytest
```

Run with verbose output:

```bash
pytest -v
```

Run a specific test file:

```bash
pytest test_client.py
```

Run a specific test class:

```bash
pytest test_client.py::TestMCPClientInitialization
```

Run a specific test:

```bash
pytest test_client.py::TestMCPClientInitialization::test_init_default_model
```

Run with coverage:

```bash
pytest --cov=. --cov-report=html
```

## Test Coverage

The test suite covers:

- **Initialization**: Default and custom configurations, authentication setup
- **Authentication**: API key, Bearer token, environment variables, precedence
- **Server Connection**: Path validation, file existence, error handling
- **Query Processing**: Tool conversion, tool calling, error handling
- **Tool Conversion**: MCP to Ollama format conversion
- **Cleanup**: Resource cleanup

## Test Structure

- `TestMCPClientInitialization`: Tests for client initialization
- `TestMCPClientAuthentication`: Tests for authentication methods
- `TestMCPClientConnectToServer`: Tests for server connection logic
- `TestMCPClientProcessQuery`: Tests for query processing and tool calling
- `TestMCPClientCleanup`: Tests for resource cleanup
- `TestMCPClientToolConversion`: Tests for tool format conversion

## Note

Some tests use mocking to avoid requiring:
- Actual MCP server running
- Ollama service running
- Network connectivity

This allows tests to run quickly and reliably in CI/CD environments.

