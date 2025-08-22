# Coffee Shop WhatsApp Bot - Makefile

.PHONY: help install test test-unit test-integration test-all lint format clean setup-dev

# Default target
help:
	@echo "Coffee Shop WhatsApp Bot - Available Commands:"
	@echo ""
	@echo "Setup & Installation:"
	@echo "  make install        Install dependencies"
	@echo "  make setup-dev      Setup development environment"
	@echo ""
	@echo "Testing:"
	@echo "  make test           Run all tests"
	@echo "  make test-unit      Run unit tests only"
	@echo "  make test-integration  Run integration tests only"
	@echo "  make test-legacy    Run legacy integration tests"
	@echo ""
	@echo "Code Quality:"
	@echo "  make lint           Run code linting"
	@echo "  make format         Format code"
	@echo ""
	@echo "Maintenance:"
	@echo "  make clean          Clean up temporary files"

# Python executable - adjust based on your system
PYTHON = /opt/homebrew/bin/python3
VENV_DIR = venv
VENV_PYTHON = $(VENV_DIR)/bin/python
VENV_PIP = $(VENV_DIR)/bin/pip

# Installation and setup
install:
	$(PYTHON) -m venv $(VENV_DIR)
	$(VENV_PIP) install --upgrade pip
	$(VENV_PIP) install -r requirements.txt

setup-dev: install
	$(VENV_PIP) install pytest pytest-cov black flake8 mypy
	@echo "Development environment setup complete!"

# Testing
test: test-unit test-integration

test-unit:
	PYTHONPATH=/Users/bonythomas/Documents/code/coffee-shop-whatsapp-bot $(VENV_PYTHON) -m pytest tests/unit/ -v --tb=short

test-integration:
	PYTHONPATH=/Users/bonythomas/Documents/code/coffee-shop-whatsapp-bot $(VENV_PYTHON) -m pytest tests/integration/ -v --tb=short

test-all:
	PYTHONPATH=/Users/bonythomas/Documents/code/coffee-shop-whatsapp-bot $(VENV_PYTHON) -m pytest tests/ -v --tb=short --cov=src

test-legacy:
	PYTHONPATH=/Users/bonythomas/Documents/code/coffee-shop-whatsapp-bot $(VENV_PYTHON) tests/test_runner.py legacy

# Code quality
lint:
	$(VENV_PIP) install flake8 mypy || true
	$(VENV_PYTHON) -m flake8 src/ tests/ --max-line-length=88 --extend-ignore=E203,W503 || true
	$(VENV_PYTHON) -m mypy src/ --ignore-missing-imports || true

format:
	$(VENV_PIP) install black || true
	$(VENV_PYTHON) -m black src/ tests/ || true

# Maintenance
clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf .pytest_cache/
	rm -rf .coverage
	rm -rf htmlcov/

# Run the application
run:
	PYTHONPATH=/Users/bonythomas/Documents/code/coffee-shop-whatsapp-bot FLASK_ENV=development FLASK_DEBUG=1 $(VENV_PYTHON) src/main.py

# Run the application in development mode with auto-reload
run-dev:
	PYTHONPATH=/Users/bonythomas/Documents/code/coffee-shop-whatsapp-bot FLASK_ENV=development FLASK_DEBUG=1 $(VENV_PYTHON) src/main.py

# Database operations
db-init:
	PYTHONPATH=/Users/bonythomas/Documents/code/coffee-shop-whatsapp-bot $(VENV_PYTHON) -c "from src.main import app, db; app.app_context().push(); db.create_all(); print('Database initialized')"

db-reset:
	PYTHONPATH=/Users/bonythomas/Documents/code/coffee-shop-whatsapp-bot $(VENV_PYTHON) -c "from src.main import app, db; app.app_context().push(); db.drop_all(); db.create_all(); print('Database reset')"
