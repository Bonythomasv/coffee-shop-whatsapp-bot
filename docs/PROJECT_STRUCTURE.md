# Project Structure

This document outlines the professional structure of the Coffee Shop WhatsApp Bot project.

## 📁 Directory Structure

```
coffee-shop-whatsapp-bot/
├── src/                          # Source code
│   ├── __init__.py
│   ├── main.py                   # Flask application entry point
│   ├── config.py                 # Configuration settings
│   ├── models/                   # Database models
│   │   ├── __init__.py
│   │   ├── sales_cache.py
│   │   └── user.py
│   └── services/                 # Business logic services
│       ├── __init__.py
│       ├── clover_api.py         # Clover POS integration
│       ├── llm_client.py         # LLM service client
│       ├── message_processor.py  # Message processing logic
│       ├── sales_processor.py    # Sales data processing
│       └── whatsapp_client.py    # WhatsApp integration
├── tests/                        # Test suite
│   ├── __init__.py
│   ├── conftest.py              # Pytest configuration
│   ├── pytest.ini              # Pytest settings
│   ├── test_runner.py           # Test runner script
│   ├── unit/                    # Unit tests
│   │   ├── __init__.py
│   │   ├── test_clover_api.py
│   │   ├── test_llm_client.py
│   │   ├── test_message_processor.py
│   │   ├── test_sales_processor.py
│   │   └── test_whatsapp_client.py
│   └── integration/             # Integration tests
│       ├── __init__.py
│       ├── integration_test_report.md
│       ├── test_clover_integration.py
│       ├── test_db.py
│       ├── test_llm_integration.py
│       ├── test_system_integration.py
│       ├── test_webhook.py
│       └── test_whatsapp_integration.py
├── docs/                        # Documentation
│   ├── DEPLOYMENT_GUIDE.md
│   ├── ENVIRONMENT_VARIABLES.md
│   ├── PROJECT_SUMMARY.md
│   ├── README.md
│   └── TROUBLESHOOTING.md
├── venv/                        # Virtual environment
├── .gitignore                   # Git ignore rules
├── Makefile                     # Build automation
├── Procfile                     # Heroku deployment
├── app.json                     # Heroku app configuration
├── requirements.txt             # Python dependencies
└── runtime.txt                  # Python version specification
```

## 🧪 Testing Structure

### Unit Tests (`tests/unit/`)
- **Purpose**: Test individual components in isolation
- **Coverage**: Services, models, utilities
- **Framework**: unittest with mocking
- **Run Command**: `make test-unit` or `python -m pytest tests/unit/`

### Integration Tests (`tests/integration/`)
- **Purpose**: Test component interactions and end-to-end flows
- **Coverage**: API integrations, database operations, message flows
- **Framework**: Custom test runners with Flask app context
- **Run Command**: `make test-integration` or `./tests/test_runner.py legacy`

### Test Configuration
- **conftest.py**: Pytest fixtures and shared test utilities
- **pytest.ini**: Pytest configuration and markers
- **test_runner.py**: Custom test runner for different test types

## 🔧 Development Workflow

### Setup Development Environment
```bash
make setup-dev
```

### Run Tests
```bash
# All tests
make test

# Unit tests only
make test-unit

# Integration tests only
make test-integration

# Legacy integration tests
make test-legacy
```

### Code Quality
```bash
# Lint code
make lint

# Format code
make format
```

### Run Application
```bash
make run
```

## 📦 Package Structure

### Source Code Organization
- **models/**: Database models and data structures
- **services/**: Business logic and external service integrations
- **main.py**: Flask application and route definitions
- **config.py**: Configuration management

### Import Strategy
All tests use absolute imports from project root:
```python
from src.services.clover_api import CloverAPIClient
from src.models.sales_cache import SalesCache
```

## 🚀 Deployment

The project is configured for Heroku deployment with:
- **Procfile**: Web process definition
- **app.json**: Heroku app configuration
- **runtime.txt**: Python version specification
- **requirements.txt**: Production dependencies

## 📋 Available Commands

### Make Commands
- `make help`: Show available commands
- `make install`: Install dependencies
- `make setup-dev`: Setup development environment
- `make test`: Run all tests
- `make test-unit`: Run unit tests
- `make test-integration`: Run integration tests
- `make lint`: Run code linting
- `make format`: Format code
- `make clean`: Clean temporary files
- `make run`: Run the application
- `make db-init`: Initialize database
- `make db-reset`: Reset database

### Test Runner Commands
```bash
./tests/test_runner.py unit          # Run unit tests
./tests/test_runner.py integration   # Run integration tests
./tests/test_runner.py all          # Run all tests
./tests/test_runner.py legacy       # Run legacy integration tests
```

## 🔍 Test Coverage

### Current Test Status
- **System Integration**: 8/9 tests passing (88.9% success rate)
- **Unit Tests**: Comprehensive coverage of core services
- **Integration Tests**: End-to-end workflow validation
- **Mock Support**: All external services properly mocked

### Test Reports
Integration test reports are generated in `tests/integration/integration_test_report.md`

This professional structure ensures maintainability, testability, and scalability of the Coffee Shop WhatsApp Bot project.
