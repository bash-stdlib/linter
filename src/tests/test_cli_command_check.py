import unittest
from unittest.mock import MagicMock, patch

from cli.commands.check import LintCommand


class TestLintCommand(unittest.TestCase):

    @patch("cli.commands.check.load_cache")
    @patch("linter.Linter")
    def test_execute__valid_files__calls_linter_correctly(
        self,
        mock_linter_class: MagicMock,
        mock_load: MagicMock,
    ) -> None:
        mock_load.return_value = {"functions": [], "namespaces": []}
        mock_linter = mock_linter_class.return_value
        mock_linter.lint.return_value = []

        args = MagicMock()
        args.command = "check"
        args.files = ["file1.sh"]
        args.format = "json"
        command = LintCommand()

        with patch("builtins.print"):
            command.execute(args)

        mock_linter.lint.assert_called_once_with("file1.sh")


if __name__ == "__main__":
    unittest.main()
