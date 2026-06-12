import unittest
from unittest.mock import mock_open, patch

from linter import Linter
from tests.assets.linter.comments.metadata import METADATA


class TestLinterComments(unittest.TestCase):
    def setUp(self) -> None:
        self.metadata = METADATA
        self.linter = Linter(self.metadata)

    def test_lint__line_starting_with_comment__returns_no_issues(self) -> None:
        content = '# stdlib.echo "hello"\n'

        with patch("builtins.open", mock_open(read_data=content)):
            issues = self.linter.lint("test.sh")

        self.assertEqual(len(issues), 0)

    def test_lint__complex_comments__does_not_break_function_scopes(self) -> None:
        content = (
            "#!/bin/bash\n"
            "\n"
            "#   (default=\"$'^([^:]+:[0-9]+|environment:[0-9]+):.+$'\").\n"
            "# @stderr The error message if the assertion fails.\n"
            "reproduce_bug1() {\n"
            "  #\n"
            "  :\n"
            "}\n"
            "\n"
            "\n"
            "debug1() {\n"
            "  #\n"
            "  :\n"
            "}\n"
            "\n"
            "#   (default=\"$'^([^:]+:[0-9]+|environment:[0-9]+):.+$'\").\n"
            "reproduce_bug2() {\n"
            "  #\n"
            "  :\n"
            "}\n"
        )

        with patch("builtins.open", mock_open(read_data=content)):
            issues = self.linter.lint("test.sh")

        self.assertEqual(len(issues), 0)
        self.assertEqual(len(self.linter.file_state.function_scopes), 3)
        self.assertEqual(self.linter.file_state.function_scopes[0].name, "reproduce_bug1")
        self.assertEqual(self.linter.file_state.function_scopes[1].name, "debug1")
        self.assertEqual(self.linter.file_state.function_scopes[2].name, "reproduce_bug2")
        self.assertNotEqual(self.linter.file_state.function_scopes[0].end_line, -1)
        self.assertNotEqual(self.linter.file_state.function_scopes[1].end_line, -1)
        self.assertNotEqual(self.linter.file_state.function_scopes[2].end_line, -1)

    def test_lint__inline_comment__returns_no_issues(self) -> None:
        content = "stdlib.something # stdlib.echo\n"

        with patch("builtins.open", mock_open(read_data=content)):
            issues = self.linter.lint("test.sh")

        self.assertEqual(len(issues), 0)

    def test_lint__escaped_comment_char__is_not_treated_as_comment(self) -> None:
        content = r'stdlib.echo "\#"' + "\n"

        with patch("builtins.open", mock_open(read_data=content)):
            issues = self.linter.lint("test.sh")

        self.assertEqual(len(issues), 0)

    def test_lint__quoted_comment_char__is_not_treated_as_comment(self) -> None:
        content = 'stdlib.echo "#"\n'

        with patch("builtins.open", mock_open(read_data=content)):
            issues = self.linter.lint("test.sh")

        self.assertEqual(len(issues), 0)

    def test_lint__comment_after_semicolon__returns_no_issues(self) -> None:
        content = "stdlib.something ; # stdlib.echo\n"

        with patch("builtins.open", mock_open(read_data=content)):
            issues = self.linter.lint("test.sh")

        self.assertEqual(len(issues), 0)

    def test_lint__multiple_comments__returns_no_issues(self) -> None:
        content = "# first comment\n# stdlib.echo\n  # another one\n"

        with patch("builtins.open", mock_open(read_data=content)):
            issues = self.linter.lint("test.sh")

        self.assertEqual(len(issues), 0)


if __name__ == "__main__":
    unittest.main()
