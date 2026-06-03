import json
import unittest
from unittest.mock import MagicMock, mock_open, patch

from cache import load_cache, save_cache


class TestCache(unittest.TestCase):
    @patch("builtins.open", new_callable=mock_open)
    @patch("os.path.exists")
    def test_load_cache__file_exists__returns_parsed_data(
        self,
        mock_exists: MagicMock,
        mock_file: MagicMock,
    ) -> None:
        mock_exists.return_value = True
        mock_data = {"functions": ["stdlib.a"]}
        mock_file.return_value.read.return_value = json.dumps(mock_data)

        result = load_cache()

        self.assertEqual(result, mock_data)

    @patch("os.path.exists")
    def test_load_cache__file_missing__returns_none(
        self,
        mock_exists: MagicMock,
    ) -> None:
        mock_exists.return_value = False

        result = load_cache()

        self.assertIsNone(result)

    @patch("sys.stderr", new_callable=MagicMock)
    @patch("builtins.open", new_callable=mock_open)
    def test_save_cache__valid_metadata__writes_json_to_file(
        self,
        mock_file: MagicMock,
        mock_stderr: MagicMock,
    ) -> None:
        mock_data = {"functions": ["stdlib.a"]}

        save_cache(mock_data)

        mock_file.assert_called_once()
        handle = mock_file()
        written_content = "".join(call.args[0] for call in handle.write.call_args_list)
        self.assertEqual(json.loads(written_content), mock_data)

    @patch("sys.stderr", new_callable=MagicMock)
    @patch("builtins.open", new_callable=mock_open)
    def test_save_cache__always__prints_status_to_stderr(
        self,
        mock_file: MagicMock,
        mock_stderr: MagicMock,
    ) -> None:
        save_cache({"any": "data"})

        mock_stderr.write.assert_any_call("Cache saved to .bash_stdlib_cache.json")


if __name__ == "__main__":
    unittest.main()
