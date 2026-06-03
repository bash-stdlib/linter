import unittest
from unittest.mock import MagicMock, patch

from cli.commands.cache import RebuildCacheCommand
from exceptions.empty_cache import EmptyCacheError


class TestRebuildCacheCommand(unittest.TestCase):
    @patch("cli.commands.cache.HTMLFetcher")
    @patch("cli.commands.cache.save_cache")
    def test_execute__successful_fetch__saves_to_cache(
        self, mock_save: MagicMock, mock_fetcher_class: MagicMock
    ) -> None:
        mock_fetcher = mock_fetcher_class.return_value
        mock_fetcher.fetch.return_value = {"data": "test"}
        command = RebuildCacheCommand()

        command.execute(MagicMock())

        mock_fetcher.fetch.assert_called_once()
        mock_save.assert_called_once_with({"data": "test"})

    @patch("cli.commands.cache.HTMLFetcher")
    def test_execute__fetch_fails__raises_empty_cache_error(
        self, mock_fetcher_class: MagicMock
    ) -> None:
        mock_fetcher = mock_fetcher_class.return_value
        mock_fetcher.fetch.return_value = None
        command = RebuildCacheCommand()

        with self.assertRaises(EmptyCacheError):
            command.execute(MagicMock())


if __name__ == "__main__":
    unittest.main()
