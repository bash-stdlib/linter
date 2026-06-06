
import os
import json
from linter import Linter

def run_verification():
    # Fetch latest metadata if needed
    cache_path = "src/.bash_stdlib_cache.json"
    if not os.path.exists(cache_path):
        print("Rebuilding cache...")
        os.system("PYTHONPATH=src python3 src/main.py cache --rebuild > /dev/null 2>&1")

    with open(cache_path, "r") as f:
        metadata = json.load(f)

    linter = Linter(metadata)

    test_cases = [
        ("comment_test.sh", "# stdlib.array\necho \"keep me\"", 0, "Namespace in comment should be ignored"),
        ("test_violation.sh", "_testing.fixtures.mock arg1", 1, "Namespace call in test file should be flagged as STD003"),
        ("private_var.sh", "_my_private=1", 0, "Private variable starting with _ should be ignored"),
        ("invalid_testing.sh", "_testing.example arg1", 1, "Invalid testing function should be flagged as STD002"),
    ]

    all_passed = True
    for filename, content, expected_errors, desc in test_cases:
        with open(filename, "w") as f: f.write(content)
        errors = linter.lint(filename)
        os.remove(filename)

        passed = len(errors) == expected_errors
        status = "PASSED" if passed else "FAILED"
        print(f"[{status}] {desc} (Errors found: {len(errors)}, expected: {expected_errors})")
        if not passed:
            all_passed = False
            for e in errors:
                print(f"  - {e.CODE}: {e.message}")

    if all_passed:
        print("\nAll verification test cases passed!")
    else:
        print("\nSome verification test cases failed.")
        exit(1)

if __name__ == "__main__":
    run_verification()
