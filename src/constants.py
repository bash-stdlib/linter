"""Central configuration constants for the bash-stdlib linter."""

CACHE_FILE: "str" = ".bash_stdlib_cache.json"
STDLIB_PATTERN: "str" = r"(?<!\w)(stdlib\.[a-z0-9._]+|assert_[a-z0-9._]+|_capture\.[a-z0-9._]+|_testing\.[a-z0-9._]+|_mock\.[a-z0-9._]+|@[a-z0-9._]+)\b"
URL_STANDARD_DOC: "str" = (
    "https://bash-stdlib.readthedocs.io/en/latest/reference/src/REFERENCE_COMPLETE.html"
)
URL_TESTING_DOC: "str" = "https://bash-stdlib.readthedocs.io/en/latest/reference_testing/src/testing/REFERENCE_COMPLETE.html"
