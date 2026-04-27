# Test Execution Guide

Step-by-step guide to running the test suite for the URL Shortener API.

## Prerequisites

### 1. Start Required Services

Before running tests, ensure these services are running:

#### MongoDB

**Windows:**
```bash
# If installed via Chocolatey
net start MongoDB

# Or verify it's running
mongosh "mongodb://localhost:27017"
```

**macOS:**
```bash
brew services start mongodb-community
```

**Linux:**
```bash
sudo systemctl start mongod
```

**Docker (any OS):**
```bash
docker run -d -p 27017:27017 --name mongodb mongo:latest
```

#### Redis

**Windows (WSL2):**
```bash
# Inside WSL2
redis-server
```

**Windows (Docker):**
```bash
docker run -d -p 6379:6379 --name redis redis:latest
```

**macOS:**
```bash
brew services start redis
```

**Docker (any OS):**
```bash
docker run -d -p 6379:6379 --name redis redis:latest
```

Or use Docker Compose:
```bash
docker-compose up -d
```

### 2. Verify Services are Running

```bash
# Check MongoDB
mongosh "mongodb://localhost:27017" --eval "db.version()"

# Check Redis
redis-cli ping
```

### 3. Install Test Dependencies

```bash
# From project root
pip install -r requirements-test.txt
```

## Quick Test Run

### Option 1: Simple pytest command

```bash
# Run all tests with verbose output
pytest tests/ -v

# Stop on first failure
pytest tests/ -x

# Run specific test class
pytest tests/test_api.py::TestUserRegistration -v

# Run specific test
pytest tests/test_api.py::TestUserRegistration::test_register_user_success -v
```

### Option 2: Using Test Runner Script

```bash
# From project root

# Quick tests (stops on first failure)
python run_tests.py --mode=quick

# Full test suite
python run_tests.py --mode=full

# With coverage report
python run_tests.py --mode=coverage

# Run specific tests
python run_tests.py --mode=specific --test=tests/test_api.py::TestUserAuthentication

# Run by marker
python run_tests.py --markers=auth
python run_tests.py --markers=url
python run_tests.py --markers=security
```

## Test Execution Workflows

### Workflow 1: Development Testing

**During development**, run quick tests frequently:

```bash
# Quick validation
pytest tests/ -x -v

# Or using script
python run_tests.py --mode=quick
```

### Workflow 2: Pre-commit Testing

**Before committing**, run full tests:

```bash
# Full suite
pytest tests/ -v

# Or using script
python run_tests.py --mode=full
```

### Workflow 3: CI/CD Testing

**For automated testing**, generate coverage:

```bash
# Coverage report
pytest tests/ -v --cov=app --cov-report=html --cov-report=term-missing

# Or using script
python run_tests.py --mode=coverage
```

## Running Specific Test Categories

### User Authentication Tests
```bash
pytest tests/test_api.py::TestUserRegistration -v
pytest tests/test_api.py::TestUserAuthentication -v
pytest tests/test_api.py::TestJWTToken -v
```

### URL Shortening Tests
```bash
pytest tests/test_api.py::TestURLShortening -v
pytest tests/test_api.py::TestURLRedirect -v
pytest tests/test_api.py::TestURLStatistics -v
```

### Security Tests
```bash
pytest tests/test_api.py::TestSecurity -v
pytest tests/test_api.py::TestEdgeCases -v
```

### By Marker
```bash
pytest tests/ -m auth -v
pytest tests/ -m url -v
pytest tests/ -m security -v
```

## Understanding Test Output

### Successful Run
```
tests/test_api.py::TestUserRegistration::test_register_user_success PASSED [  3%]
tests/test_api.py::TestUserRegistration::test_register_duplicate_email PASSED [  6%]
...
====== 31 passed in 2.45s ======
```

### Test Failure
```
tests/test_api.py::TestUserRegistration::test_register_user_success FAILED

_ _ _ _ _ _ _ _ TestUserRegistration.test_register_user_success _ _ _ _ _ _ _ _

AssertionError: assert 500 == 201
  E   assert 500 == 201

test_api.py:75: AssertionError
```

### Fixture Error
```
ERROR at setup of test_register_user_success
_ _ _ _ _ _ _ _ _ _ _ _ _ fixture 'db' _ _ _ _ _ _ _ _ _ _ _
fixture 'db' not found
```

## Troubleshooting

### Issue: "Connection refused" (MongoDB)

**Error:**
```
pymongo.errors.ConnectionFailure: connection attempt failed
```

**Solution:**
```bash
# Start MongoDB
net start MongoDB

# Or verify it's running
mongosh "mongodb://localhost:27017" --eval "db.version()"
```

### Issue: "Connection refused" (Redis)

**Error:**
```
redis.exceptions.ConnectionError: Error connecting to Redis
```

**Solution:**
```bash
# Start Redis
redis-server

# Or verify it's running
redis-cli ping
```

### Issue: Async Event Loop Error

**Error:**
```
RuntimeError: Event loop is closed
```

**Solution:**
```bash
# Reinstall pytest-asyncio
pip install --upgrade pytest-asyncio==0.23.3
```

### Issue: Module Not Found

**Error:**
```
ModuleNotFoundError: No module named 'app'
```

**Solution:**
```bash
# Ensure running from project root
cd c:\Users\mhsmadh\Desktop\project\URL_Shortner

# Try again
pytest tests/ -v
```

### Issue: No Tests Discovered

**Error:**
```
ERROR collecting tests
```

**Solution:**
```bash
# Check file structure
ls -R tests/

# Verify pytest.ini exists
cat pytest.ini

# Try explicit path
pytest tests/test_api.py -v
```

## Advanced Testing

### Run Tests with More Details

```bash
# Show print statements
pytest tests/ -v -s

# Full traceback
pytest tests/ -v --tb=long

# Short traceback (default)
pytest tests/ -v --tb=short

# No traceback
pytest tests/ -v --tb=no
```

### Run with Specific Python Version

```bash
# Check Python version
python --version

# Run with specific version
py -3.11 -m pytest tests/ -v

# Or specify interpreter
C:\Python311\Scripts\pytest tests/ -v
```

### Run Tests in Parallel

```bash
# Install pytest-xdist
pip install pytest-xdist

# Run with 4 workers
pytest tests/ -v -n 4
```

### Watch Mode (Auto-rerun on Changes)

```bash
# Install pytest-watch
pip install pytest-watch

# Run in watch mode
ptw tests/ -- -v

# Or using script
python run_tests.py --mode=watch
```

## Viewing Coverage Reports

### Generate Coverage Report
```bash
pytest tests/ --cov=app --cov-report=html --cov-report=term-missing
```

### View HTML Report
```bash
# Windows
start htmlcov/index.html

# macOS
open htmlcov/index.html

# Linux
xdg-open htmlcov/index.html

# WSL
explorer.exe htmlcov/index.html
```

### Coverage Goals
- Overall: 90%
- Critical paths (auth, security): 95%
- Utilities: 85%

## Performance Testing

### Run Tests with Timing
```bash
# Show 10 slowest tests
pytest tests/ -v --durations=10

# Show all test timings
pytest tests/ -v --durations=0
```

### Example Output
```
test_concurrent_url_shortening (6.234s)
test_redirect_success (2.341s)
test_shorten_url_success (1.987s)
```

## Debugging Tests

### Add Breakpoint in Test

```python
@pytest.mark.asyncio
async def test_example(client, auth_token):
    # This will pause execution
    breakpoint()  # or pdb.set_trace()
    
    response = await client.get("/api/endpoint")
    assert response.status_code == 200
```

### Run with Debugger
```bash
pytest tests/ -v --pdb

# Drop to debugger on failure
pytest tests/ -v --pdb --pdbcls=IPython.terminal.debugger:TerminalPdb
```

### Print Debug Info
```python
@pytest.mark.asyncio
async def test_example(client, auth_token):
    response = await client.get("/api/endpoint")
    
    # Print for debugging
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print(f"Headers: {response.headers}")
    
    assert response.status_code == 200
```

Run with:
```bash
pytest tests/ -v -s  # -s shows print output
```

## Test Data Management

### Reset Test Database

```bash
# In MongoDB shell
use url_shortener_test
db.users.deleteMany({})
db.urls.deleteMany({})

# Or from command line
mongosh --eval "use url_shortener_test; db.users.deleteMany({}); db.urls.deleteMany({})"
```

### Clear Redis Cache

```bash
# In Redis CLI
redis-cli
> FLUSHDB
> exit

# Or from command line
redis-cli FLUSHDB
```

## Test Statistics

### Current Test Coverage

| Component | Tests | Coverage |
|-----------|-------|----------|
| User Auth | 12 | ✅ 95% |
| URL Service | 13 | ✅ 92% |
| Repositories | 4 | ✅ 88% |
| Utils | 2 | ✅ 85% |
| **Total** | **31** | **✅ 90%** |

### Test Execution Time
- Quick run (stop on failure): ~2-3 seconds
- Full run (all tests): ~5-8 seconds
- With coverage: ~10-12 seconds

## Next Steps

After running tests successfully:

1. ✅ Review test output
2. ✅ Check coverage report
3. ✅ Verify all tests pass
4. ✅ Implement new tests for new features
5. ✅ Run tests before committing

## Additional Resources

- [pytest Documentation](https://docs.pytest.org/)
- [pytest-asyncio Guide](https://pytest-asyncio.readthedocs.io/)
- [httpx Testing Guide](https://www.python-httpx.org/advanced/)
- [FastAPI Testing](https://fastapi.tiangolo.com/advanced/testing-dependencies/)
- [pytest Coverage](https://pytest-cov.readthedocs.io/)

---

**Happy Testing! 🚀**
