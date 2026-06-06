"""Unit tests for the linter's handling of various Bash syntax edge cases."""

import os
import unittest

from linter import Linter


class TestLinterEdgeCases(unittest.TestCase):
    def setUp(self):
        self.metadata = {
            "functions": {
                "stdlib.message.get": {"min_args": 0, "max_args": -1},
                "stdlib.string.pad.right": {"min_args": 2, "max_args": 2},
                "stdlib.string.colour": {"min_args": 2, "max_args": 2},
                "stdlib.string.query.is_empty": {"min_args": 1, "max_args": 1},
                "assert_equals": {"min_args": 2, "max_args": 2},
            },
            "namespaces": [
                "stdlib",
                "stdlib.string",
                "stdlib.string.pad",
                "stdlib.string.query",
            ],
        }
        self.linter = Linter(self.metadata)
        self.test_file = "test_edge_cases.sh"

    def tearDown(self):
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def lint_content(self, content):
        with open(self.test_file, "w") as f:
            f.write(content)

        return self.linter.lint(self.test_file)

    def test_function_definitions_ignored(self):
        content = """
stdlib.message.get() { echo hello; }
function stdlib.message.get { echo world; }
stdlib.message.get () { echo foo; }
"""
        errors = self.lint_content(content)

        self.assertEqual(len(errors), 0)

    def test_function_as_argument_ignored(self):
        content = "echo stdlib.message.get"
        errors = self.lint_content(content)

        self.assertEqual(len(errors), 0)

    def test_assignment_ignored(self):
        content = "FOO=stdlib.message.get"
        errors = self.lint_content(content)

        self.assertEqual(len(errors), 0)

    def test_line_continuation_handled(self):
        content = """
stdlib.string.colour \\
   "arg1" \\
   "arg2"
"""
        errors = self.lint_content(content)

        self.assertEqual(len(errors), 0)

    def test_nested_complex_subshell_handled(self):
        content = (
            'padded="$(stdlib.string.pad.right "$(("${3}" - "${#2}"))" "${padded}")"'
        )
        errors = self.lint_content(content)

        self.assertEqual(len(errors), 0)

    def test_namespace_and_function_ambiguity(self):
        content = 'stdlib.string.colour "red" "text"'
        errors = self.lint_content(content)

        self.assertEqual(len(errors), 0)


if __name__ == "__main__":
    unittest.main()
