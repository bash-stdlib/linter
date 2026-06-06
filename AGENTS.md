# Agent Instructions: Bash Stdlib Linter

Welcome to the Bash Stdlib Linter repository. This document provides essential information for agents working on this codebase, including architecture, coding conventions, and testing procedures.

## Project Overview

This tool is a linter for shell scripts that use the BASH standard library. It identifies invalid function calls, incorrect argument counts, and usage of private/testing functions.

## Architecture

The project follows a modular structure where responsibilities are divided by directory:

-   **`src/`**: Contains the main entry point and core orchestration logic.
-   **`src/cli/`**: Handles command-line argument parsing and dispatches commands to the appropriate logic.
-   **`src/validators/`**: Contains modular validation rules that check function calls against specific criteria.
-   **`src/parsers/`**: Implements high-level parsing logic for shell arguments and inline error suppression.
-   **`src/parsers/token_iterators/`**: Provides specialized iterators for processing shell tokens, including handling of redirects and nested shell entities.
-   **`src/errors/`**: Defines standardized error objects used to report linting violations.
-   **`src/stdlib_html/`**: Manages the retrieval and parsing of the BASH standard library documentation to maintain a local metadata cache.
-   **`src/transformers/`**: Implements content transformations used to simplify shell code before linting.

## Coding Conventions

-   **Python 3.6 Compatibility**: Strictly maintain compatibility with Python 3.6.
    -   Do **NOT** use f-strings; use `.format()`.
    -   Do **NOT** use `from __future__ import annotations`.
    -   Use string-literal type annotations (forward references) with `typing` module generics (e.g., `arg: "List[str]"`).
-   **Regex Patterns**: Use `(?<!\w)` lookbehind and `(?![a-z0-9._])` lookahead in `stdlib_call_pattern` to avoid premature truncation of function names containing dots or underscores.
-   **Testing Style**:
    -   Follow the AAA (Arrange, Act, Assert) pattern but **DO NOT** use `# Arrange`, `# Act`, or `# Assert` comments. Use empty lines to separate sections.
    -   **Naming Convention**: Test function names **MUST** follow the pattern `test_<method_name>__<scenario>__<outcome>` (e.g., `test_lint__appendum_function__returns_no_errors`).
    -   **Mocks**: Do **NOT** create physical files on disk in tests. Use `unittest.mock.mock_open` and `patch("builtins.open")` for all file system interactions.
-   **Commits**: Use terse, commitizen-friendly subject lines with brackets (e.g., `feat(COMPONENT): description`).

## Testing

Run all unit tests using:

```bash
PYTHONPATH=src python3 -m unittest discover src/tests
```

Individual test files follow the convention `src/tests/test_<feature>.py`.

## Tooling

-   **Linting/Formatting**: Use `ruff check src` and `ruff format src`. Ruff is configured in `pyproject.toml` for Python 3.6 compatibility.
