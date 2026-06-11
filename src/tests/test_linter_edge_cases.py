import unittest
from typing import List
from unittest.mock import mock_open, patch

from issues.base import LinterIssueBase
from linter import Linter
from tests.assets.linter.edge_cases.metadata import METADATA, SCRIPTS


class TestLinterEdgeCases(unittest.TestCase):
    def setUp(self) -> None:
        self.metadata = METADATA
        self.linter = Linter(self.metadata)

    def tearDown(self) -> None:
        pass

    def lint_content(self, content: str) -> List[LinterIssueBase]:
        with patch("builtins.open", mock_open(read_data=content)):
            linter = Linter(self.metadata)
            return linter.lint("test.sh")

    def test_lint__function_definitions__ignored(self) -> None:
        content = SCRIPTS["function_definitions"]

        issues = self.lint_content(content)

        self.assertEqual(len(issues), 0)

    def test_lint__function_as_argument__ignored(self) -> None:
        content = SCRIPTS["function_as_argument"]

        issues = self.lint_content(content)

        self.assertEqual(len(issues), 0)

    def test_lint__assignment__ignored(self) -> None:
        content = SCRIPTS["assignment"]

        issues = self.lint_content(content)

        self.assertEqual(len(issues), 0)

    def test_lint__line_continuation__handled(self) -> None:
        content = SCRIPTS["line_continuation"]

        issues = self.lint_content(content)

        self.assertEqual(len(issues), 0)

    def test_lint__nested_complex_subshell__handled(self) -> None:
        content = SCRIPTS["nested_complex_subshell"]

        issues = self.lint_content(content)

        self.assertEqual(len(issues), 0)

    def test_lint__namespace_and_function_ambiguity__ignored(self) -> None:
        content = SCRIPTS["namespace_and_function_ambiguity"]

        issues = self.lint_content(content)

        self.assertEqual(len(issues), 0)


if __name__ == "__main__":
    unittest.main()
