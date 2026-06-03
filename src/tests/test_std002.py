import unittest

from errors.std002 import STD002


class TestSTD002(unittest.TestCase):

    def test_format_message__no_suggestion__returns_basic_message(
            self) -> None:
        error = STD002(
            "test.sh",
            1,
            1,
            "stdlib.a.b",
            "stdlib.a",
            suggestion=None,
        )

        message = error.format_message()

        self.assertEqual(
            message,
            "Invalid function 'stdlib.a.b' in valid namespace 'stdlib.a'.",
        )

    def test_format_message__with_suggestion__includes_suggestion(
            self) -> None:
        error = STD002(
            "test.sh",
            1,
            1,
            "stdlib.a.b",
            "stdlib.a",
            suggestion="stdlib.a.c",
        )

        message = error.format_message()

        self.assertIn("Did you mean 'stdlib.a.c'?", message)

    def test_to_dict__always__contains_expected_metadata(self) -> None:
        error = STD002("test.sh", 1, 1, "match", "ns")

        result = error.to_dict()

        self.assertEqual(result["code"], "STD002")
        self.assertEqual(result["title"], "invalid function")


if __name__ == "__main__":
    unittest.main()
