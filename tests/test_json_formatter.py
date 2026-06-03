import json
import unittest

from errors.std003 import STD003
from formatters.json_formatter import JSONFormatter


class TestJSONFormatter(unittest.TestCase):
    def setUp(self) -> None:
        self.formatter = JSONFormatter()

    def test_format__single_issue__returns_json_array(self) -> None:
        issue = STD003("test.sh", 1, 1, "stdlib.ns")

        result = self.formatter.format([issue])

        data = json.loads(result)
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["code"], "STD003")


if __name__ == "__main__":
    unittest.main()
