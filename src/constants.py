"""Central configuration constants for the bash-stdlib linter."""

ARRAY_MULTI_PLACEHOLDER: "str" = "__ARRAY_MULTI_X__"
ARRAY_SINGLE_PLACEHOLDER: "str" = "__ARRAY_SINGLE_X__"
ARRAY_SIZE_PREFIX: "str" = "__ARRAY_SIZE_"
ARRAY_SIZE_SUFFIX: "str" = "__"

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

URL_MOCK_OBJECT_DOC: "str" = "https://bash-stdlib.readthedocs.io/en/latest/reference_testing/src/testing/mock/REFERENCE_MOCK_OBJECT.html"
URL_STANDARD_DOC: "str" = (
    "https://bash-stdlib.readthedocs.io/en/latest/reference/src/REFERENCE_COMPLETE.html"
)
URL_TESTING_DOC: "str" = "https://bash-stdlib.readthedocs.io/en/latest/reference_testing/src/testing/REFERENCE_COMPLETE.html"
