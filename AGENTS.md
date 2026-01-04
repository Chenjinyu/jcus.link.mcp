# Repository Guidelines

## Project Structure & Module Organization

- `src/`: application code, organized by feature area (config, core, handlers, services, tools, models).
- `tests/`: pytest suite; unit/integration tests live alongside fixtures.
- `docs/`: project documentation and design notes.
- `examples/`: sample payloads and usage examples.
- `run_server.py` and `src/main.py`: entry points for local development.

## Build, Test, and Development Commands

Use the Makefile as the source of truth:

```bash
make install-dev     # Install dev dependencies via uv
make run             # Run the server (python -m src.main)
make run-reload      # Run with auto-reload via uvicorn
make test            # Run pytest suite
make test-coverage   # Run tests with coverage reports
make format          # Black + ruff auto-fix
make lint            # Ruff + pyright
```

If you prefer direct commands: `pytest tests/`, `uvicorn src.main:app --reload`, and `uv sync` are supported.

## Coding Style & Naming Conventions

- Indentation: 4 spaces, Python 3.11+.
- Formatting: `black` (line length 88 per `pyproject.toml`).
- Linting: `ruff`; typing: `pyright`.
- Naming: `snake_case` for functions/vars, `PascalCase` for classes, `UPPER_SNAKE_CASE` for constants.
- Prefer explicit type hints for public APIs and service interfaces.

## Testing Guidelines

- Framework: `pytest` with `pytest-asyncio` (see `pyproject.toml`).
- Test discovery: `test_*.py` or `*_test.py`; functions `test_*`; classes `Test*`.
- Markers: `unit`, `integration`, `slow` (deselect slow with `-m "not slow"`).
- Coverage: use `make test-coverage` to generate `htmlcov/` and `coverage.xml`.

## Commit & Pull Request Guidelines

- Commit messages in history are descriptive sentences (no enforced conventional format). Keep them concise and specific (e.g., "Add vector search caching").
- PRs should include: clear description, linked issue (if any), test results, and config changes. Add screenshots only for UI-affecting changes.

## Security & Configuration Tips

- Copy `.env.example` to `.env` and keep secrets out of Git.
- Use `.env` for API keys and local overrides; do not hardcode credentials.
