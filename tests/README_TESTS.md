# Drink Service - Test Suite Documentation

## Overview

This test suite provides comprehensive coverage for the Drink Service API, including:
- Unit tests for individual endpoints
- Integration tests for complete workflows
- Negative test cases for error handling
- Edge case testing
- Performance and concurrency tests

## Test Structure

```
tests/
├── conftest.py                    # Pytest fixtures and configuration
├── test_drinks_comprehensive.py   # Comprehensive drinks API tests
├── test_prices_comprehensive.py   # Comprehensive prices API tests
├── test_health_comprehensive.py   # Health check endpoint tests
├── test_root_endpoint.py          # Root endpoint tests
├── test_integration_full_flow.py  # End-to-end integration tests
├── drinks/
│   ├── test_drinks_api.py         # Original positive tests
│   └── test_drinks_negative.py    # Original negative tests
├── prices/
│   ├── test_prices_api.py          # Original positive tests
│   ├── test_prices_negative.py     # Original negative tests
│   └── test_price_by_id.py        # Price by ID tests
└── health/
    └── test_healthcheck.py         # Original health tests
```

## Running Tests

### Prerequisites

1. Install dependencies:
```bash
pip install -r requirements.txt
pip install pytest requests  # If not already installed
```

2. Set environment variable:
```bash
# For testing environment
export FLASK_CONFIG=testing

# Or for development
export FLASK_CONFIG=development
```

### Run All Tests

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run with detailed output
pytest -vv

# Run with coverage (if pytest-cov installed)
pytest --cov=app --cov-report=html
```

### Run Specific Test Files

```bash
# Run only drinks tests
pytest tests/test_drinks_comprehensive.py

# Run only prices tests
pytest tests/test_prices_comprehensive.py

# Run only health tests
pytest tests/test_health_comprehensive.py

# Run only integration tests
pytest tests/test_integration_full_flow.py
```

### Run Specific Test Classes

```bash
# Run specific test class
pytest tests/test_drinks_comprehensive.py::TestGetAllDrinks

# Run specific test method
pytest tests/test_drinks_comprehensive.py::TestGetAllDrinks::test_get_all_drinks_success
```

### Run Tests by Marker

```bash
# Run only fast tests (if markers are defined)
pytest -m fast

# Run only slow tests
pytest -m slow

# Skip integration tests
pytest -m "not integration"
```

## Test Categories

### 1. Drinks API Tests (`test_drinks_comprehensive.py`)

**TestGetAllDrinks**
- Success cases
- Empty list handling
- Response structure validation
- Content-Type verification

**TestGetDrinkById**
- Valid ID retrieval
- Not found (404) handling
- Invalid ID type handling
- Edge cases (zero, negative IDs)

**TestCreateDrink**
- Successful creation
- Minimal data creation
- Missing required fields
- Empty/whitespace validation
- Duplicate name handling
- Long name/description
- Special characters
- Unicode support
- Data persistence verification

**TestDrinksIntegration**
- Create and list flow
- CRUD operations flow

### 2. Prices API Tests (`test_prices_comprehensive.py`)

**TestGetAllPrices**
- Success cases
- Empty list handling
- Response structure validation
- Data type verification

**TestGetPriceById**
- Valid ID retrieval
- Not found handling
- Invalid ID type handling

**TestCreatePrice**
- Successful creation
- With/without end date
- Missing required fields
- Invalid drink_id
- Negative/zero amounts
- Invalid date formats
- Date range validation
- Decimal precision
- Data persistence verification

**TestPricesIntegration**
- Create and list flow
- Multiple prices per drink

### 3. Health Check Tests (`test_health_comprehensive.py`)

**TestHealthEndpoint**
- Success response
- Response structure
- Timestamp format validation
- Content-Type verification
- Method not allowed
- Performance testing
- Concurrent requests
- No authentication required

### 4. Root Endpoint Tests (`test_root_endpoint.py`)

**TestRootEndpoint**
- Success response
- Response structure
- Content-Type verification
- Method restrictions

### 5. Integration Tests (`test_integration_full_flow.py`)

**TestFullWorkflow**
- Complete create-drink-add-price flow
- Multiple prices per drink
- Error handling across workflow
- Data consistency
- Concurrent operations
- Health check during operations

## Test Fixtures

### `base_url` (session-scoped)
Provides the base URL for API requests based on `FLASK_CONFIG`:
- `development` → `http://localhost:5001`
- `testing` → `http://localhost:5002`
- `production` → `http://localhost:5003`

### `app` (session-scoped)
Creates Flask application instance with test database.

### `client` (session-scoped)
Flask test client for direct route testing.

### `api_context` (session-scoped)
Playwright API context for HTTP testing.

### `test_drink_id` (function-scoped, in prices tests)
Creates a test drink and returns its ID for price testing.

## Test Data Management

### Unique Test Data
Tests use `uuid.uuid4()` to generate unique names and avoid conflicts:
```python
unique_name = f"Test Drink {uuid.uuid4()}"
```

### Database Isolation
- Tests use the test database configured in `TestingConfig`
- Each test should clean up after itself or use unique identifiers
- Database is created/dropped per test session

## Writing New Tests

### Example Test Structure

```python
import pytest
import requests

class TestMyFeature:
    """Test suite for my feature"""
    
    def test_my_feature_success(self, base_url):
        """Test successful case"""
        response = requests.get(f"{base_url}/my-endpoint")
        assert response.status_code == 200
        data = response.json()
        assert "expected_field" in data
    
    def test_my_feature_error(self, base_url):
        """Test error case"""
        response = requests.get(f"{base_url}/my-endpoint/999")
        assert response.status_code == 404
```

### Best Practices

1. **Use descriptive test names**: `test_create_drink_with_valid_data`
2. **One assertion per concept**: Group related assertions
3. **Test both success and failure**: Include negative test cases
4. **Use fixtures**: Leverage `base_url` and other fixtures
5. **Clean up test data**: Use unique identifiers or clean up after tests
6. **Document edge cases**: Add comments for complex test scenarios
7. **Test response structure**: Verify all expected fields exist
8. **Test data types**: Ensure response data types are correct

## Common Test Patterns

### Testing Success Cases
```python
def test_success(self, base_url):
    response = requests.get(f"{base_url}/endpoint")
    assert response.status_code == 200
    data = response.json()
    assert "expected_field" in data
```

### Testing Error Cases
```python
def test_not_found(self, base_url):
    response = requests.get(f"{base_url}/endpoint/999")
    assert response.status_code == 404
    data = response.json()
    assert "message" in data
```

### Testing Validation
```python
def test_validation_error(self, base_url):
    payload = {"invalid": "data"}
    response = requests.post(f"{base_url}/endpoint", json=payload)
    assert response.status_code == 400
```

### Testing Data Persistence
```python
def test_persistence(self, base_url):
    # Create
    create_response = requests.post(f"{base_url}/endpoint", json=payload)
    assert create_response.status_code == 201
    item_id = create_response.json()["id"]
    
    # Retrieve
    get_response = requests.get(f"{base_url}/endpoint/{item_id}")
    assert get_response.status_code == 200
    assert get_response.json()["id"] == item_id
```

## Troubleshooting

### Tests Fail with Connection Error
- Ensure the service is running on the expected port
- Check `FLASK_CONFIG` environment variable
- Verify the service is accessible at the base URL

### Tests Fail with Database Errors
- Check database configuration in `app/config.py`
- Ensure test database exists or can be created
- Verify database permissions

### Tests Fail Due to Duplicate Data
- Use `uuid.uuid4()` for unique identifiers
- Clean up test data after tests
- Use isolated test databases

### Tests Are Slow
- Use Flask test client for unit tests instead of HTTP requests
- Reduce number of database operations
- Use fixtures efficiently (session-scoped when possible)

## Continuous Integration

### GitHub Actions Example

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.13'
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest requests
      - name: Run tests
        env:
          FLASK_CONFIG: testing
        run: pytest -v
```

## Coverage Goals

- **Unit Tests**: 80%+ coverage
- **Integration Tests**: All critical workflows
- **Edge Cases**: All identified edge cases
- **Error Handling**: All error paths

## Contributing

When adding new features:
1. Write tests first (TDD approach)
2. Ensure all tests pass
3. Maintain or improve coverage
4. Update this documentation if needed


