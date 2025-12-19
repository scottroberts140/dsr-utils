# Testing Guide - dsr-utils

## Running Tests

### Install test dependencies
```bash
pip install -e ".[test]"
```

### Run all tests
```bash
pytest
```

### Run tests with coverage report
```bash
pytest --cov=src/dsr_utils --cov-report=html
```

### Run specific test file
```bash
pytest tests/test_formatting.py
```

### Run tests matching a pattern
```bash
pytest -k "test_formatting"
```

### Run tests with verbose output
```bash
pytest -v
```

## Test Structure

Tests are organized by module:
- `tests/test_formatting.py` - Tests for formatting utilities
- `tests/test_strings.py` - Tests for string utilities

## Writing Tests

All test files should:
1. Start with `test_` prefix
2. Use pytest conventions
3. Include docstrings explaining what is being tested
4. Use fixtures from `conftest.py` when needed

Example:
```python
def test_function_name():
    """Concise description of what this test verifies."""
    assert some_condition
```

## Coverage Reports

After running tests with coverage, view the HTML report:
```bash
open htmlcov/index.html
```
