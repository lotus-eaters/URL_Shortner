# URL Shortener - Development Guide

## Quick Start

### Prerequisites

- Python 3.11+
- Docker & Docker Compose
- Git

### Local Development Setup

1. **Clone and Setup**

```bash
cd /Users/hsmadhusudhan/Desktop/FastAPI/URL_Shortner
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

2. **Configure Environment**

```bash
cp .env.example .env
# Edit .env with your settings
```

3. **Start Services with Docker Compose**

```bash
docker-compose up -d
```

This will start:

- FastAPI server on http://localhost:8000
- MongoDB on localhost:27017
- Redis on localhost:6379
- Prometheus on http://localhost:9090
- Grafana on http://localhost:3000

4. **Access the Application**

- API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- Grafana: http://localhost:3000 (admin/admin)

### Running Tests

```bash
pytest tests/ -v
```

### Stopping Services

```bash
docker-compose down
```

## Development Workflow

### Running App in Debug Mode

```bash
source venv/bin/activate
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Viewing Logs

```bash
docker-compose logs -f api
```

### Database Connection

```bash
# MongoDB
mongosh "mongodb://admin:password@localhost:27017"

# Redis
redis-cli -p 6379
```

## API Endpoints (Chapter 5 onwards)

Will be documented as we build them!

## Monitoring & Metrics

- Prometheus: http://localhost:9090
- Grafana: http://localhost:3000
- Application metrics: http://localhost:8000/metrics

## Deployment

See `.github/workflows/` for CI/CD configuration.

---

# URL_Shortner - Project Structure

```
URL_Shortner/
│
├── 📁 app/                              # Main application package
│   ├── __init__.py
│   │
│   ├── 📁 core/                         # Core configuration & infrastructure
│   │   ├── __init__.py
│   │   ├── config.py                    # Settings management (Pydantic)
│   │   ├── database.py                  # MongoDB & Redis connection
│   │   └── logger.py                    # Structured logging setup
│   │
│   ├── 📁 api/                          # HTTP API Layer
│   │   ├── __init__.py
│   │   ├── 📁 controllers/              # Request handlers
│   │   │   └── __init__.py
│   │   └── 📁 routes/                   # API endpoint definitions
│   │       └── __init__.py
│   │
│   ├── 📁 services/                     # Business Logic Layer
│   │   ├── __init__.py
│   │   # (URL shortening, validation, caching logic)
│   │
│   ├── 📁 repositories/                 # Data Access Layer
│   │   ├── __init__.py
│   │   # (MongoDB & Redis operations)
│   │
│   ├── 📁 models/                       # Database Models
│   │   ├── __init__.py
│   │   # (User, URL schemas for MongoDB)
│   │
│   ├── 📁 schemas/                      # Pydantic Validation Schemas
│   │   ├── __init__.py
│   │   └── schemas.py                   # Request/Response models
│   │
│   ├── 📁 middleware/                   # Custom Middleware
│   │   └── __init__.py                  # (JWT auth, logging, error handling)
│   │
│   └── 📁 utils/                        # Utility Functions
│       └── __init__.py                  # (MD5 hashing, validators)
│
├── 📁 tests/                            # Testing
│   # (Unit tests, integration tests, fixtures)
│
├── 📁 docker/                           # Docker Configuration
│   ├── Dockerfile                       # App container image
│   └── prometheus.yml                   # Prometheus monitoring config
│
├── 📁 .github/                          # GitHub Configuration
│   └── 📁 workflows/                    # CI/CD Pipelines (Chapter 8)
│       # (GitHub Actions workflows)
│
├── 📄 main.py                           # FastAPI Application Entry Point
├── 📄 docker-compose.yml               # Multi-container Orchestration
├── 📄 requirements.txt                  # Python Dependencies
├── 📄 .env.example                      # Environment Variables Template
├── 📄 .gitignore                        # Git Ignore Rules
```

### 📊 Data Flow for URL Shortening

```
1. Client sends POST request with original URL
           ↓
2. Controller receives and validates request
           ↓
3. Service layer processes URL (MD5 hashing)
           ↓
4. Repository checks Redis cache first (fast)
           ↓
5. If not cached, queries MongoDB (persistent)
           ↓
6. Response returned to client with short code
           ↓
7. Future redirects fetch from cache (99% faster)
```
