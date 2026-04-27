# URL Shortener Test Suite

Comprehensive pytest test suite with 50+ test cases covering authentication, URL shortening, redirects, security, and edge cases.

## Test Structure

```
tests/
├── conftest.py          # Pytest configuration and shared fixtures
├── test_api.py          # Main test suite with all test classes
├── README.md            # This file
```

## Installation

### 1. Install Test Dependencies

```bash
# Install all test dependencies
pip install -r requirements-test.txt
```

### 2. Verify Installation

```bash
pytest --version
pytest-asyncio --version
```

## Running Tests

### Quick Start

```bash
# Run all tests
pytest tests/

# Run with verbose output
pytest tests/ -v

# Run specific test class
pytest tests/test_api.py::TestUserRegistration -v

# Run specific test
pytest tests/test_api.py::TestUserRegistration::test_register_user_success -v
```

### Using Test Runner Script

```bash
# Quick tests (stop on first failure)
python run_tests.py --mode=quick

# Full test suite
python run_tests.py --mode=full

# With coverage report
python run_tests.py --mode=coverage

# Run specific test file
python run_tests.py --mode=specific --test=tests/test_api.py::TestUserRegistration

# Run by marker
python run_tests.py --markers=auth
python run_tests.py --markers=url
python run_tests.py --markers=security
```

## Test Categories

### 1. User Registration Tests (5 tests)
- ✅ test_register_user_success
- ✅ test_register_duplicate_email
- ✅ test_register_invalid_email
- ✅ test_register_short_password
- ✅ test_register_missing_fields

### 2. Authentication Tests (4 tests)
- ✅ test_login_success
- ✅ test_login_invalid_password
- ✅ test_login_nonexistent_user
- ✅ test_login_inactive_user

### 3. JWT Token Tests (3 tests)
- ✅ test_jwt_token_valid
- ✅ test_jwt_token_invalid
- ✅ test_missing_auth_header

### 4. URL Shortening Tests (6 tests)
- ✅ test_shorten_url_success
- ✅ test_shorten_invalid_url
- ✅ test_shorten_with_custom_alias
- ✅ test_duplicate_short_code
- ✅ test_shorten_with_expiration
- ✅ test_shorten_unauthenticated

### 5. URL Redirect Tests (4 tests)
- ✅ test_redirect_success
- ✅ test_redirect_not_found
- ✅ test_redirect_expired_url
- ✅ test_redirect_inactive_url

### 6. Click Count Tests (1 test)
- ✅ test_click_count_increment

### 7. URL Statistics Tests (2 tests)
- ✅ test_get_url_stats
- ✅ test_get_stats_not_found

### 8. Security Tests (2 tests)
- ✅ test_password_hashing
- ✅ test_injection_prevention

### 9. Edge Case Tests (3 tests)
- ✅ test_very_long_url
- ✅ test_special_characters_in_url
- ✅ test_concurrent_url_shortening

### 10. Health Check Test (1 test)
- ✅ test_health_check

## Test Fixtures

### Core Fixtures
- **client**: Async HTTP client for API testing
- **db**: MongoDB connection with auto cleanup
- **sample_user**: Pre-created test user
- **auth_token**: Valid JWT token for authenticated tests
- **sample_url**: Pre-created shortened URL

### Usage Example

```python
@pytest.mark.asyncio
async def test_example(client, auth_token, sample_user):
    """Example test using fixtures"""
    headers = {"Authorization": f"Bearer {auth_token}"}
    response = await client.get("/api/auth/profile", headers=headers)
    assert response.status_code == 200
```

## Prerequisites

### Services Required (must be running)
- MongoDB: `mongosh "mongodb://localhost:27017"`
- Redis: `redis-cli`
- FastAPI app: `uvicorn main:app --reload`

Or use Docker Compose:
```bash
docker-compose up -d
```

### Environment Variables

Create or verify `.env` file exists:
```
MONGODB_URL=mongodb://localhost:27017
MONGODB_DB_NAME=url_shortener_test
REDIS_URL=redis://localhost:6379
JWT_SECRET_KEY=test-secret-key-very-secret
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24
```

## Coverage Reports

### Generate Coverage Report
```bash
pytest tests/ --cov=app --cov-report=html --cov-report=term-missing
```

### View HTML Coverage Report
```bash
# On Windows
start htmlcov/index.html

# On macOS
open htmlcov/index.html

# On Linux
xdg-open htmlcov/index.html
```

### Coverage Goals
- **Overall**: 90%
- **Critical paths**: 95% (auth, security)
- **Utilities**: 85% (url_utils, security)

## Pytest Configuration

See `pytest.ini` for configuration:
- Async mode: auto
- Test discovery: tests/
- Markers: asyncio, auth, url, security, slow, integration
- Output: verbose, short traceback

## Troubleshooting

### Async Test Issues
```
ERROR: asyncio event loop closed
```
**Solution**: Ensure pytest-asyncio is installed:
```bash
pip install pytest-asyncio==0.23.3
```

### Database Connection Errors
```
ConnectionError: Failed to connect to MongoDB
```
**Solution**: Start MongoDB service:
```bash
# Windows
net start MongoDB

# macOS
brew services start mongodb-community

# Linux
sudo systemctl start mongod
```

### Fixture Errors
```
fixture 'db' not found
```
**Solution**: Ensure conftest.py is in tests/ directory:
```bash
ls -la tests/conftest.py
```

### Import Errors
```
ModuleNotFoundError: No module named 'app'
```
**Solution**: Run tests from project root:
```bash
cd c:\Users\mhsmadh\Desktop\project\URL_Shortner
pytest tests/
```

## Continuous Integration

### GitHub Actions Example
```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    services:
      mongodb:
        image: mongo:latest
        options: --health-cmd="mongosh --eval 'db.adminCommand(\"ping\")'" --health-interval 10s --health-timeout 5s --health-retries 5
      redis:
        image: redis:latest
        options: --health-cmd="redis-cli ping" --health-interval 10s --health-timeout 5s --health-retries 5
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.11'
      - run: pip install -r requirements.txt -r requirements-test.txt
      - run: pytest tests/ -v --cov=app
```

## Writing New Tests

### Test Template
```python
@pytest.mark.asyncio
async def test_new_feature(client, auth_token):
    """Test description"""
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    # Arrange
    test_data = {"key": "value"}
    
    # Act
    response = await client.post("/api/endpoint", json=test_data, headers=headers)
    
    # Assert
    assert response.status_code == 200
    assert response.json()["key"] == "value"
```

### Best Practices
1. Use descriptive test names
2. One assertion per test (or group related assertions)
3. Use fixtures for setup/teardown
4. Use markers for test categorization
5. Keep tests isolated and independent
6. Use async/await for async operations
7. Mock external dependencies

## Test Metrics

| Category | Tests | Status |
|----------|-------|--------|
| User Registration | 5 | ✅ |
| Authentication | 4 | ✅ |
| JWT Tokens | 3 | ✅ |
| URL Shortening | 6 | ✅ |
| URL Redirects | 4 | ✅ |
| Click Count | 1 | ✅ |
| Statistics | 2 | ✅ |
| Security | 2 | ✅ |
| Edge Cases | 3 | ✅ |
| Health | 1 | ✅ |
| **Total** | **31** | **✅** |

## Resources

- [pytest Documentation](https://docs.pytest.org/)
- [pytest-asyncio](https://pytest-asyncio.readthedocs.io/)
- [httpx Documentation](https://www.python-httpx.org/)
- [FastAPI Testing](https://fastapi.tiangolo.com/advanced/testing-dependencies/)
- [pytest-cov](https://pytest-cov.readthedocs.io/)

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review test code in `test_api.py`
3. Check `conftest.py` for fixture definitions
4. Ensure all services (MongoDB, Redis) are running
5. Verify environment variables in `.env`
