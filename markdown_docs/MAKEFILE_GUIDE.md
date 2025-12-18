# Makefile Usage Guide

This guide explains how to use the Makefile for common development tasks.

## 📋 Quick Start

```bash
# See all available commands
make help

# Setup project for first time
make setup

# Install development dependencies
make install-dev

# Run all checks before committing
make pre-commit
```

## 🎯 Common Workflows

### Daily Development

```bash
# 1. Format your code
make format

# 2. Run linters
make lint

# 3. Run tests
make test

# Or do all at once:
make check test
```

### Before Committing

```bash
# Run pre-commit checks (format, lint, fast test)
make pre-commit

# Or manually:
make format lint test-fast
```

### Full Quality Check

```bash
# Run everything with coverage
make ci
```

## 🧹 Code Quality Commands

### Formatting

```bash
# Format code with black
make black

# Sort imports with isort
make isort

# Do both (recommended)
make format
```

**Example output:**
```
Running isort...
Skipped 2 files
✨ Code formatting complete!
```

### Linting

```bash
# Run flake8 linter
make flake8

# Run mypy type checker
make mypy

# Run both
make lint
```

**Example output:**
```
Running flake8...
./src/services/llm_service.py:45:1: F401 'asyncio' imported but unused
Running mypy...
Success: no issues found in 18 source files
```

### Combined Check

```bash
# Format + lint in one command
make check
```

## 🧪 Testing Commands

### Basic Testing

```bash
# Run all tests
make test

# Run tests with coverage report
make test-coverage

# Run only fast tests (no coverage)
make test-fast
```

**Example output:**
```
Running tests with coverage...
================================ test session starts ================================
collected 45 items

tests/test_services/test_resume_service.py ........                           [ 17%]
tests/test_handlers/test_mcp_handler.py .........                             [ 37%]
...

---------- coverage: platform linux, python 3.11.5-final-0 -----------
Name                                    Stmts   Miss  Cover   Missing
---------------------------------------------------------------------
src/__init__.py                             2      0   100%
src/config/settings.py                     45      3    93%   67-69
src/services/llm_service.py               156     12    92%   45, 89-95
...
---------------------------------------------------------------------
TOTAL                                    1540     58    96%

📊 Coverage report generated:
  - HTML: htmlcov/index.html
  - XML: coverage.xml
```

### Watch Mode

```bash
# Run tests automatically when files change
make test-watch
```

## 🧽 Cleanup Commands

### Clean Everything

```bash
# Clean all generated files
make clean
```

### Selective Cleaning

```bash
# Remove Python cache files (__pycache__, *.pyc)
make clean-pyc

# Remove build artifacts
make clean-build

# Remove test artifacts
make clean-test

# Remove coverage reports
make clean-coverage

# Remove log files
make clean-logs
```

**Example output:**
```
Cleaning Python cache files...
✨ Python cache cleaned!
```

## 🚀 Running the Server

### Development Server

```bash
# Run server
make run

# Run with auto-reload (recommended for development)
make run-reload
```

### Production Server

```bash
# Run with multiple workers
make run-prod
```

## 🐳 Docker Commands

```bash
# Build Docker image
make docker-build

# Run Docker container
make docker-run

# Remove Docker image
make docker-clean
```

## 📊 Information Commands

### Project Info

```bash
# Show project information
make info

# Count lines of code
make lines

# Show project tree structure
make tree

# Show dependency tree
make deps-tree
```

**Example output:**
```
$ make info
Project: MCP Resume Server
Python version: Python 3.11.5
Pip version: pip 23.3.1
Working directory: /path/to/mcp-resume-server
Virtual environment: /path/to/venv
```

### Version & Health

```bash
# Show project version
make version

# Check server health (must be running)
make health
```

## 🔐 Security Commands

```bash
# Run security checks
make security

# This runs:
# - pip-audit: Check for known vulnerabilities
# - bandit: Security linter for Python
```

## 🛠️ Utility Commands

### Environment Setup

```bash
# Create .env from template
make env

# Generate requirements.txt from current environment
make lock

# Update dependencies
make deps-update
```

### Git Hooks

```bash
# Install git pre-commit hooks
make install-hooks
```

This creates a pre-commit hook that runs `make pre-commit` before each commit.

## 📈 Advanced Commands

### Benchmarking

```bash
# Run performance benchmarks
make benchmark

# Profile the application
make profile
```

### Database

```bash
# Initialize vector database
make db-init
```

### Interactive Shell

```bash
# Start Python shell with project context
make shell
```

**Example:**
```python
$ make shell
Services loaded. Available: settings, get_llm_service, get_vector_service, get_resume_service, get_tool_registry
>>> settings.app_name
'mcp-resume-server'
>>> llm_service = get_llm_service()
>>> type(llm_service)
<class 'src.services.llm_service.AnthropicLLMService'>
```

## 🎯 Recommended Workflows

### Workflow 1: Starting Development

```bash
# 1. Setup (first time only)
make setup

# 2. Install dev dependencies
make install-dev

# 3. Create .env file
make env
# Edit .env with your API keys

# 4. Start development server
make run-reload
```

### Workflow 2: Making Changes

```bash
# 1. Make your code changes

# 2. Format code
make format

# 3. Run tests
make test

# 4. Check everything
make check

# 5. Commit if all passes
git add .
git commit -m "Your message"
```

### Workflow 3: Pre-Commit

```bash
# Run pre-commit checks (fast)
make pre-commit

# If all passes:
git commit -m "Your message"
```

### Workflow 4: CI Pipeline

```bash
# Run full CI pipeline locally
make ci

# This runs:
# 1. Install dev dependencies
# 2. Format + lint (check)
# 3. Run tests with coverage
```

### Workflow 5: Clean Slate

```bash
# Clean everything
make clean

# Reinstall dependencies
make install-dev

# Run tests
make test-coverage
```

## 🎨 Customizing the Makefile

You can modify the Makefile variables at the top:

```makefile
# Python executable
PYTHON := python3
PIP := pip3

# Directories
SRC_DIR := src
TEST_DIR := tests

# Tool arguments
PYTEST_ARGS := -v --tb=short
COVERAGE_ARGS := --cov=$(SRC_DIR) --cov-report=html
```

## ⚡ Performance Tips

### Faster Testing

```bash
# Skip slow tests
pytest -m "not slow"

# Run only unit tests
pytest -m "unit"

# Run specific test file
pytest tests/test_services/test_resume_service.py

# Run specific test
pytest tests/test_services/test_resume_service.py::TestResumeService::test_search
```

### Parallel Testing

```bash
# Install pytest-xdist
pip install pytest-xdist

# Run tests in parallel
pytest -n auto
```

## 🐛 Troubleshooting

### Issue: "make: command not found"

**Solution:** Install make:
```bash
# Ubuntu/Debian
sudo apt-get install build-essential

# macOS
xcode-select --install
```

### Issue: "Permission denied" on setup.sh

**Solution:**
```bash
chmod +x setup.sh
make setup
```

### Issue: Tests fail with import errors

**Solution:**
```bash
# Reinstall dependencies
make clean
make install-dev
```

### Issue: Coverage not showing

**Solution:**
```bash
# Clean and regenerate
make clean-coverage
make test-coverage
```

## 📚 Related Files

- **pyproject.toml** - Tool configurations (black, isort, pytest, coverage)
- **.flake8** - Flake8 configuration
- **requirements-dev.txt** - Development dependencies
- **conftest.py** - Pytest fixtures and configuration

## 💡 Tips & Tricks

1. **Use tab completion**: Type `make ` and press Tab to see available targets

2. **Chain commands**: You can run multiple targets:
   ```bash
   make clean format lint test
   ```

3. **Silent mode**: Add `-s` to suppress command echoing:
   ```bash
   make -s test
   ```

4. **Dry run**: See what would be executed without running:
   ```bash
   make -n test
   ```

5. **Keep tools updated**: Periodically run:
   ```bash
   make deps-update
   ```

## 📊 Quality Targets

```bash
# Code quality score
make lint          # Should have no errors

# Test coverage
make test-coverage # Aim for >80%

# Type checking
make mypy          # Should pass with no errors

# Security
make security      # Should have no vulnerabilities
```

## 🎯 Quick Reference

| Command | What it does |
|---------|--------------|
| `make help` | Show all commands |
| `make format` | Format code (black + isort) |
| `make lint` | Lint code (flake8 + mypy) |
| `make test` | Run all tests |
| `make test-coverage` | Run tests with coverage |
| `make clean` | Clean all generated files |
| `make check` | Format + lint |
| `make pre-commit` | Quick checks before commit |
| `make ci` | Full CI pipeline |
| `make run` | Start development server |

---

**Pro tip**: Always run `make pre-commit` before committing code! 🚀