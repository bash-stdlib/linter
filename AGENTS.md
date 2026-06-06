# Agent Instructions: Bash Stdlib Linter

## Architecture
- **`src/`**: Entry point, core orchestration.
- **`src/cli/`**: CLI parsing and command dispatch.
- **`src/validators/`**: Modular validation rules.
- **`src/parsers/`**: High-level argument and ignore parsing.
- **`src/parsers/transformers/`**: Pre-parsing code simplifications.
- **`src/parsers/token_iterators/`**: Token-level shell iterators.
- **`src/errors/`**: Standardized error objects.
- **`src/stdlib_html/`**: Documentation scraping and metadata cache.

## Coding Conventions
- **Python 3.6+**: Use `.format()`, no f-strings. No `from __future__ import annotations`. Use string-literal type hints.
- **Regex**: Use `(?<!\w)` lookbehind and `(?![a-z0-9._])` lookahead for function matching.
- **Testing**:
  - Pattern: `test_<method>__<scenario>__<outcome>`.
  - Style: AAA without comments; use empty line separators.
  - Isolation: No disk I/O; use `mock_open` and `patch`.
  - Execution: Every test file must end with:
    ```python
    if __name__ == "__main__":
        unittest.main()
    ```
- **Commits**: `feat(COMPONENT): description`. Terse and commitizen-friendly.

## Testing & Tooling
- **Run all**: `PYTHONPATH=src python3 -m unittest discover src/tests`
- **Mypy**: `mypy src` (configured in `pyproject.toml`).
- **Formatting**: `ruff check src`, `ruff format src` (Py3.6 target).
