import os
import sys
from typing import Any

# Add src to sys.path
sys.path.insert(0, os.path.abspath("src"))

from linter import Linter

metadata = {
    "functions": {
        "stdlib.array.assert.is_array": {
            "name": "stdlib.array.assert.is_array",
            "arguments": ["$1"],
            "keywords": [],
            "globals": [],
            "min_args": 1,
            "max_args": 1,
        },
    },
    "namespaces": [
        "stdlib",
        "stdlib.array",
        "stdlib.array.assert",
    ],
}

def reproduce():
    linter = Linter(metadata)
    filepath = "reproduce_issue.sh"

    print(f"Linting {filepath}...")
    with open(filepath, "r") as f:
        print("File content:")
        print("---")
        print(f.read())
        print("---")

    errors = linter.lint(filepath)

    if not errors:
        print("No errors found.")
    else:
        for error in errors:
            print(f"[{error.CODE}] {error.file}:{error.line}:{error.column} - {error.message}")

if __name__ == "__main__":
    reproduce()
