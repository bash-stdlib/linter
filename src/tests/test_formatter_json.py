import json
import unittest

from issues.errors.STD003 import STD003
from formatters.json_formatter import JSONFormatterBase


class TestJSONFormatterBase(unittest.TestCase):
    def setUp(self) -> None:
        self.formatter = JSONFormatterBase()

    def test_format__single_issue__returns_json_array(self) -> None:
        issue = STD003("test.sh", 1, 1, "stdlib.ns")

        result = self.formatter.format([issue])

        data = json.loads(result)
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["code"], "STD003")
        self.assertEqual(data[0]["severity"], "error")


if __name__ == "__main__":
    unittest.main()
