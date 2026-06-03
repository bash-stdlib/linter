import unittest
from unittest.mock import MagicMock, patch

from cli.commands.lint import LintCommand


class TestLintCommand(unittest.TestCase):
    @patch("cli.commands.lint.load_cache")
    @patch("linter.Linter")
    def test_execute__valid_files__calls_linter_correctly(
        self, mock_linter_class, mock_load
    ):
        mock_load.return_value = {"functions": [], "namespaces": []}
        mock_linter = mock_linter_class.return_value
        mock_linter.lint.return_value = []

        args = MagicMock()
        args.files = ["file1.sh"]
        command = LintCommand()

        with patch("builtins.print"):
            command.execute(args)

        mock_linter.lint.assert_called_once_with("file1.sh")


if __name__ == "__main__":
    unittest.main()
