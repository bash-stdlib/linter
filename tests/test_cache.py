import unittest
import json
from unittest.mock import patch, mock_open
from cache import save_cache, load_cache

class TestCache(unittest.TestCase):
    @patch('builtins.open', new_callable=mock_open)
    @patch('os.path.exists')
    def test_load_cache__file_exists__returns_parsed_data(self, mock_exists, mock_file):
        mock_exists.return_value = True
        mock_data = {"functions": ["stdlib.a"]}
        mock_file.return_value.read.return_value = json.dumps(mock_data)

        result = load_cache()

        self.assertEqual(result, mock_data)

    @patch('os.path.exists')
    def test_load_cache__file_missing__returns_none(self, mock_exists):
        mock_exists.return_value = False

        result = load_cache()

        self.assertIsNone(result)

    @patch('builtins.open', new_callable=mock_open)
    def test_save_cache__valid_metadata__writes_json_to_file(self, mock_file):
        mock_data = {"functions": ["stdlib.a"]}

        save_cache(mock_data)

        mock_file.assert_called_once()
        handle = mock_file()
        written_content = "".join(call.args[0] for call in handle.write.call_args_list)
        self.assertEqual(json.loads(written_content), mock_data)

if __name__ == "__main__":
    unittest.main()
