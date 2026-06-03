import unittest

from errors.std000 import STD000


class TestSTD000(unittest.TestCase):
    def test_format_message__valid_exception__returns_correct_message(self):
        error = STD000("test.sh", "Permission denied")

        message = error.format_message()

        self.assertEqual(message, "Failed to read file: Permission denied")

    def test_to_dict__always__contains_expected_metadata(self):
        error = STD000("test.sh", "Error")

        result = error.to_dict()

        self.assertEqual(result["code"], "STD000")
        self.assertEqual(result["title"], "system error")
        self.assertEqual(result["file"], "test.sh")


if __name__ == "__main__":
    unittest.main()
