# Pharma Management Service Tests

This directory contains tests for the Pharma Management Service.

## Test Structure

- `unit/`: Unit tests for individual components
- `integration/`: Integration tests for API endpoints
- `conftest.py`: Test fixtures and configuration
- `run_tests.py`: Script to run tests with coverage reporting

## Running Tests

### Run all tests

```bash
python -m tests.run_tests
```

### Run specific test types

```bash
# Run only unit tests
python -m tests.run_tests -m unit

# Run only integration tests
python -m tests.run_tests -m integration

# Run tests for a specific module
python -m tests.run_tests tests/unit/test_pharmacy_service.py
```

### Run with Docker

```bash
docker-compose exec app python -m tests.run_tests
```

## Test Coverage

After running tests, a coverage report will be generated in the `coverage_html` directory.

## Adding New Tests

1. Create a new test file in the appropriate directory (`unit/` or `integration/`)
2. Use the naming convention `test_*.py` for test files
3. Use the appropriate fixtures from `conftest.py`
4. Add appropriate markers to categorize your tests