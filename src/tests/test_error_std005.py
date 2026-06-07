import unittest

from errors.base import Severity
from errors.std005 import STD005


class TestSTD005(unittest.TestCase):
    def test_format_message__valid_exception__returns_correct_message(self) -> None:
        error = STD005("test.sh", 1, 1, "cmd", 1, 2, 2)

        self.assertEqual(error.SEVERITY, Severity.ERROR)
        self.assertEqual(error.CODE, "STD005")
        self.assertIn("'cmd' expects 2 arguments, but 1 were provided.", error.message)

    def test_to_dict__always__contains_expected_metadata(self) -> None:
        error = STD005("test.sh", 1, 1, "cmd", 1, 2, 2)

        result = error.to_dict()

        self.assertEqual(result["severity"], "error")
        self.assertEqual(result["code"], "STD005")


if __name__ == "__main__":
    unittest.main()
