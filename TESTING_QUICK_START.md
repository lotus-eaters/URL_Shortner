# Testing Quick Start

Get running with tests in 5 minutes.

## 0️⃣ Install Dependencies (Optional - Only if not installed)

### MongoDB Installation

**Easiest: Use Docker (all platforms)**
```bash
docker run -d -p 27017:27017 mongo:latest
```

**Or install natively:**

**Windows:**
- Download from: https://www.mongodb.com/try/download/community
- Run installer, follow setup wizard
- Or use Chocolatey: `choco install mongodb`

**macOS:**
```bash
brew tap mongodb/brew
brew install mongodb-community
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get update
sudo apt-get install -y mongodb
```

### Redis Installation

**Using Docker:**
```bash
docker run -d -p 6379:6379 redis:latest
```

**Or install natively:**
- Windows: Download from https://github.com/microsoftarchive/redis/releases or use Docker
- macOS: `brew install redis`
- Linux: `sudo apt-get install redis-server`

## 1️⃣ Start Services (2 min)

```bash
# Terminal 1: Start MongoDB
# Windows
net start MongoDB

# macOS (if installed via Homebrew)
brew services start mongodb-community

# Linux (Ubuntu/Debian)
sudo systemctl start mongod

# Or use Docker (all platforms)
docker run -d -p 27017:27017 mongo:latest

# Terminal 2: Start Redis (use Docker if not installed)
docker run -d -p 6379:6379 redis:latest

# Or start FastAPI app in Terminal 3
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## 2️⃣ Install Test Tools (1 min)

```bash
pip install -r requirements-test.txt
```

## 3️⃣ Run Tests (2 min)

```bash
# Option A: Quick command
pytest tests/ -v

# Option B: Using script
python run_tests.py --mode=full

# Option C: Specific tests
pytest tests/test_api.py::TestUserRegistration -v
```

## 📊 Expected Output

```
tests/test_api.py::TestUserRegistration::test_register_user_success PASSED
tests/test_api.py::TestUserRegistration::test_register_duplicate_email PASSED
...
====== 31 passed in 5.23s ======
```

## 📋 Test Categories

```bash
# Auth tests only
pytest tests/test_api.py::TestUserAuthentication -v

# URL tests only
pytest tests/test_api.py::TestURLShortening -v

# Security tests only
pytest tests/test_api.py::TestSecurity -v

# By marker
pytest tests/ -m auth -v
pytest tests/ -m url -v
pytest tests/ -m security -v
```

## 🔍 Coverage Report

```bash
# Generate HTML coverage
pytest tests/ --cov=app --cov-report=html --cov-report=term-missing

# View report
start htmlcov/index.html  # Windows
```

## ⚡ Common Commands

```bash
# Run all tests
pytest tests/

# Verbose output
pytest tests/ -v

# Stop on first failure
pytest tests/ -x

# Show print statements
pytest tests/ -v -s

# Specific test class
pytest tests/test_api.py::TestUserRegistration -v

# Specific test
pytest tests/test_api.py::TestUserRegistration::test_register_user_success -v

# Coverage report
pytest tests/ --cov=app --cov-report=term-missing

# With timing
pytest tests/ --durations=10
```

## 🐛 Troubleshooting

| Error | Fix |
|-------|-----|
| MongoDB connection refused | Windows: `net start MongoDB` / macOS: `brew services start mongodb-community` / Linux: `sudo systemctl start mongod` / Docker: `docker run -d -p 27017:27017 mongo:latest` |
| Redis connection refused | `docker run -d -p 6379:6379 redis:latest` |
| Module not found | Ensure you're in project directory and venv activated |
| Event loop closed | `pip install --upgrade pytest-asyncio` |

## 📚 More Info

- Full guide: [TEST_EXECUTION_GUIDE.md](TEST_EXECUTION_GUIDE.md)
- Tests structure: [tests/README.md](tests/README.md)
- Test documentation: [TEST_CASES.md](TEST_CASES.md)

## ✅ Test Stats

- **Total tests**: 31
- **Test categories**: 10
- **Coverage target**: 90%
- **Expected time**: 5-10 seconds

**Ready? Let's test! 🚀**
