import unittest

from errors.std001 import STD001


class TestSTD001(unittest.TestCase):
    def test_format_message__invalid_namespace__returns_correct_message(self) -> None:
        error = STD001("test.sh", 1, 1, "stdlib.wrong.func", "stdlib.wrong")

        message = error.format_message()

        self.assertEqual(message, "Invalid namespace 'stdlib.wrong'.")

    def test_to_dict__always__contains_expected_metadata(self) -> None:
        error = STD001("test.sh", 1, 1, "match", "ns")

        result = error.to_dict()

        self.assertEqual(result["code"], "STD001")
        self.assertEqual(result["title"], "invalid namespace")


if __name__ == "__main__":
    unittest.main()
