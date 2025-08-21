# Repository Guidelines

## Project Structure & Module Organization

- **Source code**: All main modules are under `src/tabelogmcp/`.
- **Tests**: Comprehensive tests are found in the `tests/` directory. Key files test models, functionality, CLI integration, and error handling.
- **Examples**: Sample usage scripts live in `examples/` (e.g. `basic_search.py`, `cli_example.py`).
- **Entry point**: The main CLI is exposed via the `tabelogmcp` script.
- **Assets**: All additional assets should reside alongside their relevant code.

## Build, Test, and Development Commands

- `make lint` — Run code style checks using ruff.
- `make type` — Check typing using mypy.
- `make test` — Run all tests with pytest and coverage.
- `uv run pytest -v -s --cov=src tests` — Run verbose test suite with coverage.
- `make publish` — Build and publish the package.

## Coding Style & Naming Conventions

- **Language**: Python 3.12+
- **Indentation**: 4 spaces.
- **Line length**: Max 120 chars (ruff)
- **Linting**: Use `ruff` with various plugin checks (see `pyproject.toml`). Auto-import sorting enforced.
- **Typing**: Type hints and mypy are required.
- **Naming**: Use snake_case for functions/variables, PascalCase for types/models. Test files prefixed with `test_`.

## Testing Guidelines

- **Frameworks**: Pytest, pytest-asyncio, pytest-cov.
- **Test Coverage**: Target 90%+ coverage (current: ~94%).
- **Locations**: Place unit/integration tests in the `tests/` folder. Name files as `test_*.py`.
- **Run**: `make test` or `uv run pytest -v`.
- **Fixtures/Async**: Use fixtures and `AsyncMock` for HTTP and boundary tests.

## Commit & Pull Request Guidelines

- **Commits**: Keep messages short and descriptive (e.g., `fix`, `init commit`).
- **Pull requests**: Clearly describe changes, reference any related issues, and provide screenshots or examples if front-end/CLI changes.
- **Checklist**: Ensure all tests pass, code is formatted, and coverage does not drop.

## Security & Configuration Tips

- Honor Tabelog’s robots.txt and ToS.
- Implement rate limiting if scraping at scale.
- Sensitive configs should be managed via environment variables and not committed.

## License

MIT License. See LICENSE file for details.
