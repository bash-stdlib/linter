"""Central configuration constants for the bash-stdlib linter."""

CACHE_FILE: "str" = ".bash_stdlib_cache.json"
SHELL_COMMAND_SEPARATORS = {
    ";",
    "|",
    "&",
    "&&",
    "||",
    "(",
    ")",
    "{",
    "}",
    "\n",
    "`",
    "#",
}
"""Tokens that act as delimiters between separate shell commands."""

URL_STANDARD_DOC: "str" = (
    "https://bash-stdlib.readthedocs.io/en/latest/reference/src/REFERENCE_COMPLETE.html"
)
URL_TESTING_DOC: "str" = "https://bash-stdlib.readthedocs.io/en/latest/reference_testing/src/testing/REFERENCE_COMPLETE.html"
URL_MOCK_OBJECT_DOC: "str" = "https://bash-stdlib.readthedocs.io/en/latest/reference_testing/src/testing/mock/REFERENCE_MOCK_OBJECT.html"

GLOBAL_GRANTING_FUNCTIONS = {"setup", "setup_suite"}
"""Functions that grant mocks global visibility within a test file."""
