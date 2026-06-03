import unittest
from unittest.mock import patch, MagicMock
from cli.commands.rebuild import RebuildCacheCommand
from cli.commands.lint import LintCommand
from cli.commands.list_codes import ListErrorCodesCommand
from errors import EmptyCacheError

class TestCommands(unittest.TestCase):
    @patch('cli.commands.rebuild.HTMLFetcher')
    @patch('cli.commands.rebuild.save_cache')
    def test_rebuild_cache_command__successful_fetch__saves_to_cache(self, mock_save, mock_fetcher_class):
        mock_fetcher = mock_fetcher_class.return_value
        mock_fetcher.fetch.return_value = {"data": "test"}
        command = RebuildCacheCommand()

        command.execute(None)

        mock_fetcher.fetch.assert_called_once()
        mock_save.assert_called_once_with({"data": "test"})

    @patch('cli.commands.rebuild.HTMLFetcher')
    def test_rebuild_cache_command__fetch_fails__raises_empty_cache_error(self, mock_fetcher_class):
        mock_fetcher = mock_fetcher_class.return_value
        mock_fetcher.fetch.return_value = None
        command = RebuildCacheCommand()

        with self.assertRaises(EmptyCacheError):
            command.execute(None)

    @patch('cli.commands.lint.load_cache')
    @patch('linter.Linter')
    def test_lint_command__valid_files__calls_linter_correctly(self, mock_linter_class, mock_load):
        mock_load.return_value = {"functions": [], "namespaces": []}
        mock_linter = mock_linter_class.return_value
        mock_linter.lint.return_value = []
        args = MagicMock()
        args.check = ["file1.sh"]
        command = LintCommand()

        with patch('builtins.print'):
            command.execute(args)

        mock_linter.lint.assert_called_once_with("file1.sh")

    def test_list_error_codes_command__always__prints_all_codes(self):
        command = ListErrorCodesCommand()

        with patch('builtins.print') as mock_print:
            command.execute(None)

            # Check if a known code and its description were printed
            calls = [call.args[0] for call in mock_print.call_args_list if call.args]
            output = "\n".join(calls)
            self.assertIn("STD001", output)
            self.assertIn("invalid namespace", output)

if __name__ == "__main__":
    unittest.main()
