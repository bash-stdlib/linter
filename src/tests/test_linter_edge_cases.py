import unittest
from typing import List
from unittest.mock import mock_open, patch

from errors.base import LinterIssueBase
from linter import Linter


class TestLinterEdgeCases(unittest.TestCase):
    def setUp(self) -> None:
        self.metadata = {
            "functions": {
                "stdlib.foo": {
                    "name": "stdlib.foo",
                    "min_args": 0,
                    "max_args": 0,
                },
                "stdlib.bar": {
                    "name": "stdlib.bar",
                    "min_args": 1,
                    "max_args": 1,
                },
            },
            "namespaces": ["stdlib"],
        }
        self.linter = Linter(self.metadata)

    def tearDown(self) -> None:
        pass

    def lint_content(self, content: str) -> List[LinterIssueBase]:
        with patch("builtins.open", mock_open(read_data=content)):
            linter = Linter(self.metadata)
            return linter.lint("test.sh")

    def test_function_definitions_ignored(self) -> None:
        content = (
            "function stdlib.foo() {\n  echo hello\n}\nstdlib.foo () {\n  echo hi\n}"
        )

        issues = self.lint_content(content)

        self.assertEqual(len(issues), 0)

    def test_function_as_argument_ignored(self) -> None:
        content = "echo stdlib.foo"

        issues = self.lint_content(content)

        self.assertEqual(len(issues), 0)

    def test_assignment_ignored(self) -> None:
        content = "VAR=stdlib.foo"

        issues = self.lint_content(content)

        self.assertEqual(len(issues), 0)

    def test_line_continuation_handled(self) -> None:
        content = "stdlib.bar \\\n  arg1"

        issues = self.lint_content(content)

        self.assertEqual(len(issues), 0)

    def test_nested_complex_subshell_handled(self) -> None:
        content = 'nested="${HELLO:-"$(stdlib.foo)"}"'

        issues = self.lint_content(content)

        self.assertEqual(len(issues), 0)

    def test_namespace_and_function_ambiguity(self) -> None:
        content = "stdlib.foo"

        issues = self.lint_content(content)

        self.assertEqual(len(issues), 0)


if __name__ == "__main__":
    unittest.main()
