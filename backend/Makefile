.PHONY: install sync dev test format lint clean run-api run-invoice run-template

# Installation & Setup
install:
	uv sync

sync:
	uv sync

dev:
	uv sync --extra dev

# Running Services
run-api:
	uv run uvicorn src.API.DocumentGenAPI:app --reload --port 8000

run-invoice:
	uv run uvicorn src.API.InvoiceGenAPI:app --reload --port 8080

run-template:
	uv run uvicorn src.API.TemplateGenAPI:app --reload --port 8081

# Development Tools
format:
	uv run ruff format .
	uv run black .

lint:
	uv run ruff check .

lint-fix:
	uv run ruff check --fix .

type-check:
	uv run pyright src

type-check-mypy:
	uv run mypy src

# Testing
test:
	uv run pytest

test-cov:
	uv run pytest --cov=src --cov-report=html --cov-report=term-missing

# Cleanup
clean:
	rm -rf .venv
	rm -rf .pytest_cache
	rm -rf .ruff_cache
	rm -rf .mypy_cache
	rm -rf htmlcov
	rm -rf dist
	rm -rf build
	rm -rf *.egg-info
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

# Environment
env-check:
	@echo "Checking .env file..."
	@test -f .env && echo "✅ .env exists" || echo "❌ .env missing - copy .env.example to .env"
	@test -f .env && grep -q "OPENAI_API_KEY=sk-" .env && echo "✅ OPENAI_API_KEY set" || echo "❌ OPENAI_API_KEY not set"
	@test -f .env && grep -q "STRAPI_BEARER_TOKEN=" .env && echo "✅ STRAPI_BEARER_TOKEN set" || echo "❌ STRAPI_BEARER_TOKEN not set"

# Help
help:
	@echo "Available commands:"
	@echo "  make install       - Install dependencies with uv"
	@echo "  make dev           - Install with dev dependencies"
	@echo "  make run-api       - Start DocumentGenAPI (port 8000)"
	@echo "  make run-invoice   - Start InvoiceGenAPI (port 8080)"
	@echo "  make run-template  - Start TemplateGenAPI (port 8081)"
	@echo "  make format        - Format code with ruff & black"
	@echo "  make lint          - Lint code with ruff"
	@echo "  make lint-fix      - Fix linting issues automatically"
	@echo "  make test          - Run tests"
	@echo "  make test-cov      - Run tests with coverage"
	@echo "  make clean         - Remove caches and build artifacts"
	@echo "  make env-check     - Check .env configuration"
