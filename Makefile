# Makefile for MCP Resume Server
# Provides common development tasks: Formatting, Linting, Typing, Testing, Cleanup
# stack: 
# - Formatting: black - Industry standard code formatter
# - Linting:    ruff - Fast, replaces flake8, isort, pyflakes, pylint, etc.
# - Typing:     pyright - Fast type checker (VS Code native)
# - Tests:      pytest - Most popular testing framework
# - Coverage:   pytest-cov - Coverage reports for pytest
# - Virtual Env: uv - Manage dependencies and virtual environments

.PHONY: help install install-dev lint ruff ruff-fix black mypy test test-coverage clean all check run


# Default target
.DEFAULT_GOAL := help

# Python and pip executables
PYTHON := python3
PIP := pip3

# Project directories
SRC_DIR := src
TEST_DIR := tests

# Tool configurations
PYTEST_ARGS := -v --tb=short
COVERAGE_ARGS := --cov=$(SRC_DIR) --cov-report=html --cov-report=term-missing --cov-report=xml

##@ General
help: ## Display this help message
	@echo "MCP Resume Server - Development Makefile"
	@echo ""
	@awk 'BEGIN {FS = ":.*##"; printf "\nUsage:\n  make \033[36m<target>\033[0m\n"} /^[a-zA-Z_-]+:.*?##/ { printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2 } /^##@/ { printf "\n\033[1m%s\033[0m\n", substr($$0, 5) } ' $(MAKEFILE_LIST)


##@ Installation
install: ## Install production dependencies
	@echo "Installing production dependencies with uv..."
	@uv sync --no-dev

install-dev: ## Install development dependencies (includes testing, linting tools)
	@echo "Installing development dependencies with uv..."
	@uv sync

##@ Code Quality. switch mypy to pyright which is more powerful and faster
lint: ruff pyright ## Run all linters (ruff + pyright)

ruff: ## Run ruff linter
	@echo "Running ruff..."
	@ruff check $(SRC_DIR) $(TEST_DIR)

ruff-fix: ## Run ruff with auto-fix
	@echo "Running ruff (auto-fix)..."
	@ruff check $(SRC_DIR) $(TEST_DIR) --fix

pyright: ## Run mypy type checker
	@echo "Running pyright..."
	@pyright $(SRC_DIR)

# same as make pyright
typecheck: pyright ## Run pyright type checker

black: ## Format code with black
	@echo "Running black..."
	@black $(SRC_DIR) $(TEST_DIR) --line-length=100

format: black ruff-fix ## Format code (black + ruff auto-fix)
	@echo "✨ Code formatting complete!"

check: format lint ## Format and lint code
	@echo "✅ Code quality check complete!"

##@ Testing
test: ## Run tests without coverage
	@echo "Running tests..."
	@pytest $(TEST_DIR) $(PYTEST_ARGS)

test-coverage: ## Run tests with coverage report
	@echo "Running tests with coverage..."
	@pytest $(TEST_DIR) $(PYTEST_ARGS) $(COVERAGE_ARGS)
	@echo ""
	@echo "📊 Coverage report generated:"
	@echo "  - HTML: htmlcov/index.html"
	@echo "  - XML: coverage.xml"

test-watch: ## Run tests in watch mode (requires pytest-watch)
	@echo "Running tests in watch mode..."
	@ptw $(TEST_DIR) -- $(PYTEST_ARGS)

test-fast: ## Run tests without coverage (fastest)
	@echo "Running fast tests..."
	@pytest $(TEST_DIR) -q

##@ Cleanup
clean: clean-pyc clean-build clean-test clean-coverage ## Clean all generated files
clean-pyc: ## Remove Python cache files
	@echo "Cleaning Python cache files..."
	@find . -type f -name '*.py[co]' -delete
	@find . -type d -name '__pycache__' -delete
	@find . -type d -name '*.egg-info' -exec rm -rf {} + 2>/dev/null || true
	@echo "✨ Python cache cleaned!"

clean-build: ## Remove build artifacts
	@echo "Cleaning build artifacts..."
	@rm -rf build/
	@rm -rf dist/
	@rm -rf .eggs/
	@find . -name '*.egg' -exec rm -f {} +
	@echo "✨ Build artifacts cleaned!"

clean-test: ## Remove test artifacts
	@echo "Cleaning test artifacts..."
	@rm -rf .pytest_cache/
	@rm -rf .tox/
	@rm -f .coverage
	@echo "✨ Test artifacts cleaned!"

clean-coverage: ## Remove coverage reports
	@echo "Cleaning coverage reports..."
	@rm -rf htmlcov/
	@rm -rf coverage.xml
	@rm -rf .coverage
	@echo "✨ Coverage reports cleaned!"

clean-logs: ## Remove log files
	@echo "Cleaning log files..."
	@rm -rf logs/*.log
	@echo "✨ Log files cleaned!"

##@ Development
run: ## Run development server
	@echo "Starting development server..."
	@$(PYTHON) -m src.main

run-fastmcp: ## Run FastMCP server (recommended)
	@echo "Starting FastMCP server..."
	@$(PYTHON) -m src.main_fastmcp

run-reload: ## Run development server with auto-reload
	@echo "Starting development server with auto-reload..."
	@uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

run-prod: ## Run production server
	@echo "Starting production server..."
	@uvicorn src.main:app --host 0.0.0.0 --port 8000 --workers 4

shell: ## Start Python interactive shell with project context
	@$(PYTHON) -i -c "from src.config import settings; from src.services import get_llm_service, get_vector_service, get_resume_service; from src.tools import get_tool_registry; print('Services loaded. Available: settings, get_llm_service, get_vector_service, get_resume_service, get_tool_registry')"

##@ Docker
docker-build: ## Build Docker image
	@echo "Building Docker image..."
	@docker build -t mcp-resume-server:latest .

docker-run: ## Run Docker container
	@echo "Running Docker container..."
	@docker run -p 8000:8000 --env-file .env mcp-resume-server:latest

docker-clean: ## Remove Docker image
	@echo "Removing Docker image..."
	@docker rmi mcp-resume-server:latest

##@ Documentation
docs-serve: ## Serve documentation locally
	@echo "Serving documentation..."
	@$(PYTHON) -m http.server 8080 --directory .

##@ CI/CD
ci: install-dev check test-coverage ## Run CI pipeline (install, check, test with coverage)
	@echo "✅ CI pipeline complete!"

pre-commit: format lint test-fast ## Run before committing (format, lint, fast test)
	@echo "✅ Pre-commit checks passed!"

all: clean install-dev check test-coverage ## Run everything (clean, install, check, test)
	@echo "✅ All tasks complete!"

##@ Utilities
setup: ## Initial project setup
	@echo "Setting up project..."
	@bash setup.sh
	@echo "✅ Setup complete!"

env: ## Create .env from template
	@if [ ! -f .env ]; then \
		cp .env.example .env; \
		echo "✅ Created .env file. Please edit with your API keys!"; \
	else \
		echo "⚠️  .env file already exists!"; \
	fi

deps-update: ## Update dependencies
	@echo "Updating dependencies..."
	@$(PIP) list --outdated
	@echo ""
	@echo "To update a package: pip install --upgrade <package>"

deps-tree: ## Show dependency tree
	@echo "Dependency tree:"
	@pipdeptree

lock: ## Generate requirements.txt from current environment
	@echo "Generating requirements.txt..."
	@$(PIP) freeze > requirements.txt
	@echo "✅ requirements.txt updated!"

version: ## Show project version
	@$(PYTHON) -c "from src import __version__; print(f'MCP Resume Server v{__version__}')"

health: ## Check server health
	@echo "Checking server health..."
	@curl -s http://localhost:8000/health | python -m json.tool

##@ Benchmarking

benchmark: ## Run performance benchmarks
	@echo "Running benchmarks..."
	@pytest $(TEST_DIR) -v --benchmark-only

profile: ## Profile the application
	@echo "Profiling application..."
	@$(PYTHON) -m cProfile -o profile.stats src/main.py
	@$(PYTHON) -c "import pstats; p = pstats.Stats('profile.stats'); p.sort_stats('cumulative'); p.print_stats(20)"

##@ Security

security: ## Run security checks
	@echo "Running security checks..."
	@pip-audit
	@bandit -r $(SRC_DIR) -f screen

##@ Database
db-init: ## Initialize database
	@echo "Initializing database..."
	@$(PYTHON) -c "from src.services import get_vector_service; vs = get_vector_service(); print('Vector service initialized')"

##@ Information
info: ## Show project information
	@echo "Project: MCP Resume Server"
	@echo "Python version: $$($(PYTHON) --version)"
	@echo "Pip version: $$($(PIP) --version)"
	@echo "Working directory: $$(pwd)"
	@echo "Virtual environment: $${VIRTUAL_ENV:-'Not in venv'}"

lines: ## Count lines of code
	@echo "Lines of code:"
	@find $(SRC_DIR) -name "*.py" -type f -exec wc -l {} + | sort -n | tail -n 1
	@echo ""
	@echo "Breakdown by module:"
	@find $(SRC_DIR) -name "*.py" -type f -exec wc -l {} + | sort -n

tree: ## Show project tree structure
	@tree -I '__pycache__|*.pyc|*.pyo|*.egg-info|htmlcov|.pytest_cache|.mypy_cache' -L 3

##@ Git Hooks

install-hooks: ## Install git pre-commit hooks
	@echo "Installing git hooks..."
	@echo '#!/bin/bash\nmake pre-commit' > .git/hooks/pre-commit
	@chmod +x .git/hooks/pre-commit
	@echo "✅ Git hooks installed!"