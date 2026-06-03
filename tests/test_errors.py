import unittest

from errors.std000 import STD000
from errors.std001 import STD001
from errors.std002 import STD002
from errors.std003 import STD003
from errors.std004 import STD004


class TestErrors(unittest.TestCase):
    def test_std001__format_message__returns_correct_message(self) -> None:
        error = STD001("test.sh", 1, 1, "stdlib.wrong.func", "stdlib.wrong")

        self.assertEqual(error.message, "Invalid namespace 'stdlib.wrong'.")
        self.assertEqual(error.CODE, "STD001")

    def test_std002__with_suggestion__formats_correctly(self) -> None:
        error = STD002(
            "test.sh",
            5,
            2,
            "stdlib.array.is_ary",
            "stdlib.array",
            "stdlib.array.is_array",
        )

        self.assertIn("Did you mean 'stdlib.array.is_array'?", error.message)
        self.assertEqual(error.CODE, "STD002")

    def test_std003__always__formats_correctly(self) -> None:
        error = STD003("test.sh", 10, 5, "stdlib.array")

        self.assertEqual(
            error.message, "'stdlib.array' is a namespace, not a function."
        )
        self.assertEqual(error.CODE, "STD003")

    def test_std004__always__formats_correctly(self) -> None:
        error = STD004("test.sh", 1, 1, "stdlib.something")

        self.assertEqual(
            error.message, "Invalid namespace or function 'stdlib.something'."
        )
        self.assertEqual(error.CODE, "STD004")

    def test_std000__always__formats_correctly(self) -> None:
        error = STD000("missing.sh", "Permission denied")

        self.assertIn("Failed to read file", error.message)
        self.assertEqual(error.CODE, "STD000")

    def test_to_dict__always__contains_expected_metadata(self) -> None:
        error = STD001("test.sh", 1, 1, "match", "ns")

        result = error.to_dict()

        self.assertEqual(result["code"], "STD001")
        self.assertEqual(result["title"], "invalid namespace")


if __name__ == "__main__":
    unittest.main()
