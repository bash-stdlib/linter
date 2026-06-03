import unittest
from unittest.mock import patch

from cli.commands.rebuild import RebuildCacheCommand
from exceptions.empty_cache import EmptyCacheError


class TestRebuildCacheCommand(unittest.TestCase):
    @patch("cli.commands.rebuild.HTMLFetcher")
    @patch("cli.commands.rebuild.save_cache")
    def test_execute__successful_fetch__saves_to_cache(
        self, mock_save, mock_fetcher_class
    ):
        mock_fetcher = mock_fetcher_class.return_value
        mock_fetcher.fetch.return_value = {"data": "test"}
        command = RebuildCacheCommand()

        command.execute(None)

        mock_fetcher.fetch.assert_called_once()
        mock_save.assert_called_once_with({"data": "test"})

    @patch("cli.commands.rebuild.HTMLFetcher")
    def test_execute__fetch_fails__raises_empty_cache_error(self, mock_fetcher_class):
        mock_fetcher = mock_fetcher_class.return_value
        mock_fetcher.fetch.return_value = None
        command = RebuildCacheCommand()

        with self.assertRaises(EmptyCacheError):
            command.execute(None)


if __name__ == "__main__":
    unittest.main()
