.PHONY: help test lint coverage clean run

# ── ChatGPT Web Bridge — Makefile ──────────────────────

PYTHON = .venv/Scripts/python.exe
PIP = .venv/Scripts/pip.exe

help:  ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-18s\033[0m %s\n", $$1, $$2}'

install:  ## Install all dependencies
	$(PIP) install -r requirements.txt
	$(PIP) install pytest pytest-asyncio pytest-cov

test:  ## Run all tests
	$(PYTHON) -m pytest tests/ -v

test-fast:  ## Run tests without slow ones
	$(PYTHON) -m pytest tests/ -v -m "not slow"

coverage:  ## Run tests with coverage report
	$(PYTHON) -m pytest tests/ --cov=. --cov-report=term-missing

lint:  ## Lint all Python files
	$(PYTHON) -m ruff check .

typecheck:  ## Type check with mypy
	$(PYTHON) -m mypy *.py --ignore-missing-imports

clean:  ## Remove cache and temp files
	rm -rf __pycache__ .pytest_cache .mypy_cache
	rm -rf conversations.json usage.json
	find . -type d -name __pycache__ -exec rm -rf {} +

run:  ## Start server in visible mode
	$(PYTHON) server.py --port 9090

run-headless:  ## Start server in headless mode
	$(PYTHON) server.py --port 9090 --no-headless
