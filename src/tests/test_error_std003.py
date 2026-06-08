import unittest

from errors.enum import Severity
from errors.std003 import STD003


class TestSTD003(unittest.TestCase):
    def test_format_message__always__returns_correct_message(self) -> None:
        error = STD003("test.sh", 1, 1, "stdlib.array")

        self.assertEqual(
            error.message,
            "'stdlib.array' is a namespace, not a function.",
        )
        self.assertEqual(error.CODE, "STD003")
        self.assertEqual(error.SEVERITY, Severity.ERROR)

    def test_to_dict__always__contains_expected_metadata(self) -> None:
        error = STD003("test.sh", 1, 1, "match")

        result = error.to_dict()

        self.assertEqual(result["code"], "STD003")
        self.assertEqual(result["title"], "namespace called as function")
        self.assertEqual(result["severity"], Severity.ERROR.level)


if __name__ == "__main__":
    unittest.main()
