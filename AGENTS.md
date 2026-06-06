# Agent Instructions: Bash Stdlib Linter

Welcome to the Bash Stdlib Linter repository. This document provides essential information for agents working on this codebase, including architecture, coding conventions, and testing procedures.

## Project Overview

This tool is a linter for shell scripts that use the BASH standard library. It identifies invalid function calls, incorrect argument counts, and usage of private/testing functions.

## Architecture

The project follows a modular architecture:

-   **`src/main.py`**: Entry point. Enforces Python >= 3.6.
-   **`src/linter.py`**: Core orchestration. Performs single-pass linting, manages regex-based call matching, and coordinates validators.
-   **`src/cli/`**: Handles command-line arguments and command dispatching.
-   **`src/validators/`**: Contains specific validation logic (e.g., `ArgumentCountValidator`, `IsFunctionCallValidator`). All validators inherit from `ValidatorBase` and follow the Liskov Substitution Principle.
-   **`src/parsers/`**:
    -   `bash_arguments.py`: Uses a lazy, iterative pipeline of token iterators for efficient argument extraction.
    -   `comment_ignores.py`: Handles inline error suppression (`# stdlib: disable`).
-   **`src/parsers/token_iterators/`**: Granular iterators for handling shlex tokens, shell redirects, and nested entities (subshells, expansions).
-   **`src/errors/`**: Standardized error codes (STD000-STD008) defined as class-level `CODE` attributes.
-   **`src/stdlib_html/`**: Logic for fetching and parsing the BASH standard library documentation to build the metadata cache.

## Coding Conventions

-   **Python 3.6 Compatibility**: Strictly maintain compatibility with Python 3.6.
    -   Do **NOT** use f-strings; use `.format()`.
    -   Do **NOT** use `from __future__ import annotations`.
    -   Use string-literal type annotations (forward references) with `typing` module generics (e.g., `arg: "List[str]"`).
-   **Regex Patterns**: Use `(?<!\w)` lookbehind and `(?![a-z0-9._])` lookahead in `stdlib_call_pattern` to avoid premature truncation of function names containing dots or underscores.
-   **Testing Style**:
    -   Follow the AAA (Arrange, Act, Assert) pattern but **DO NOT** use `# Arrange`, `# Act`, or `# Assert` comments. Use empty lines to separate sections.
-   **Commits**: Use terse, commitizen-friendly subject lines with brackets (e.g., `feat(COMPONENT): description`).

## Key Features & Logic

-   **`--appendum` / `-a` Flag**: Allows injecting additional namespaces or functions to be ignored by the linter. Bypasses all validation and argument parsing for matches.
-   **`--ignore` / `-i` Flag**: Suppresses specific error codes globally.
-   **Inline Disables**: Supports `# stdlib: disable CODE1,CODE2`.
    -   If at the start of a line (excluding whitespace), it affects the next line.
    -   If following code on the same line, it affects only that line.
-   **Metadata Cache**: Metadata is stored in `.bash_stdlib_cache.json`. Use `PYTHONPATH=src python3 src/main.py cache --rebuild` to refresh.
-   **Coordinate System**: Error line and column numbers are 1-indexed.

## Testing

Run all unit tests using:

```bash
PYTHONPATH=src python3 -m unittest discover src/tests
```

Individual test files follow the convention `src/tests/test_<feature>.py`.

## Tooling

-   **Linting/Formatting**: Use `ruff check src` and `ruff format src`. Ruff is configured in `pyproject.toml` for Python 3.6 compatibility.
