import json
import unittest

from errors.std003 import STD003
from formatters.json_formatter import JSONFormatterBase


class TestJSONFormatterBase(unittest.TestCase):
    def setUp(self) -> None:
        self.formatter = JSONFormatterBase()

    def test_format__single_error__returns_json_array(self) -> None:
        error = STD003("test.sh", 1, 1, "stdlib.ns")

        result = self.formatter.format([error])

        data = json.loads(result)
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["severity"], "error")
        self.assertEqual(data[0]["code"], "STD003")


if __name__ == "__main__":
    unittest.main()
