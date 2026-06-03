import unittest

from errors.std004 import STD004


class TestSTD004(unittest.TestCase):
    def test_format_message__always__returns_correct_message(self):
        error = STD004("test.sh", 1, 1, "stdlib.unknown")

        message = error.format_message()

        self.assertEqual(message, "Invalid namespace or function 'stdlib.unknown'.")

    def test_to_dict__always__contains_expected_metadata(self):
        error = STD004("test.sh", 1, 1, "match")

        result = error.to_dict()

        self.assertEqual(result["code"], "STD004")
        self.assertEqual(result["title"], "unknown namespace or function")


if __name__ == "__main__":
    unittest.main()
