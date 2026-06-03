import unittest
from unittest.mock import mock_open, patch

from linter import Linter


class TestLinterComments(unittest.TestCase):
    def setUp(self) -> None:
        self.metadata = {
            "functions": {
                "stdlib.echo": {"min_args": 1, "max_args": 1},
                "stdlib.something": {"min_args": 0, "max_args": 0},
            },
            "namespaces": ["stdlib"],
        }
        self.linter = Linter(self.metadata)

    def test_lint__line_starting_with_comment__returns_no_errors(self) -> None:
        content = '# stdlib.echo "hello"\n'

        with patch("builtins.open", mock_open(read_data=content)):
            errors = self.linter.lint("test.sh")

        self.assertEqual(len(errors), 0)

    def test_lint__inline_comment__returns_no_errors(self) -> None:
        content = "stdlib.something # stdlib.echo\n"

        with patch("builtins.open", mock_open(read_data=content)):
            errors = self.linter.lint("test.sh")

        self.assertEqual(len(errors), 0)

    def test_lint__escaped_comment_char__is_not_treated_as_comment(self) -> None:
        content = r'stdlib.echo "\#"' + "\n"

        with patch("builtins.open", mock_open(read_data=content)):
            errors = self.linter.lint("test.sh")

        self.assertEqual(len(errors), 0)

    def test_lint__quoted_comment_char__is_not_treated_as_comment(self) -> None:
        content = 'stdlib.echo "#"\n'

        with patch("builtins.open", mock_open(read_data=content)):
            errors = self.linter.lint("test.sh")

        self.assertEqual(len(errors), 0)

    def test_lint__comment_after_semicolon__returns_no_errors(self) -> None:
        content = "stdlib.something ; # stdlib.echo\n"

        with patch("builtins.open", mock_open(read_data=content)):
            errors = self.linter.lint("test.sh")

        self.assertEqual(len(errors), 0)

    def test_lint__multiple_comments__returns_no_errors(self) -> None:
        content = "# first comment\n# stdlib.echo\n  # another one\n"

        with patch("builtins.open", mock_open(read_data=content)):
            errors = self.linter.lint("test.sh")

        self.assertEqual(len(errors), 0)


if __name__ == "__main__":
    unittest.main()
