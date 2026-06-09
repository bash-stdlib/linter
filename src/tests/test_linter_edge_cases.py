import unittest
from typing import List
from unittest.mock import mock_open, patch

from errors.base import LinterErrorBase
from linter import Linter
from tests.assets.linter.edge_cases.metadata import METADATA, SCRIPTS


class TestLinterEdgeCases(unittest.TestCase):
    def setUp(self) -> None:
        self.metadata = METADATA
        self.linter = Linter(self.metadata)

    def tearDown(self) -> None:
        pass

    def lint_content(self, content: str) -> List[LinterErrorBase]:
        with patch("builtins.open", mock_open(read_data=content)):
            linter = Linter(self.metadata)
            return linter.lint("test.sh")

    def test_function_definitions_ignored(self) -> None:
        content = SCRIPTS["function_definitions"]

        errors = self.lint_content(content)

        self.assertEqual(len(errors), 0)

    def test_function_as_argument_ignored(self) -> None:
        content = SCRIPTS["function_as_argument"]

        errors = self.lint_content(content)

        self.assertEqual(len(errors), 0)

    def test_assignment_ignored(self) -> None:
        content = SCRIPTS["assignment"]

        errors = self.lint_content(content)

        self.assertEqual(len(errors), 0)

    def test_line_continuation_handled(self) -> None:
        content = SCRIPTS["line_continuation"]

        errors = self.lint_content(content)

        self.assertEqual(len(errors), 0)

    def test_nested_complex_subshell_handled(self) -> None:
        content = SCRIPTS["nested_complex_subshell"]

        errors = self.lint_content(content)

        self.assertEqual(len(errors), 0)

    def test_namespace_and_function_ambiguity(self) -> None:
        content = SCRIPTS["namespace_and_function_ambiguity"]

        errors = self.lint_content(content)

        self.assertEqual(len(errors), 0)


if __name__ == "__main__":
    unittest.main()
