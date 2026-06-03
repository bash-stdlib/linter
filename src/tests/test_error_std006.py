"""Unit tests for the STD006 error."""

import unittest

from errors import STD006


class TestSTD006(unittest.TestCase):
    def test_format_message__any_call__correctly_formatted(self) -> None:
        error = STD006("file.sh", 10, 5, "stdlib.foo")

        self.assertEqual(error.message, "Failed to parse arguments for 'stdlib.foo'.")

    def test_to_dict__any_call__contains_all_fields(self) -> None:
        error = STD006("file.sh", 10, 5, "stdlib.foo")

        data = error.to_dict()

        self.assertEqual(data["code"], "STD006")
        self.assertEqual(data["file"], "file.sh")
        self.assertEqual(data["line"], 10)
        self.assertEqual(data["column"], 5)
        self.assertEqual(data["match"], "stdlib.foo")
        self.assertIn("message", data)


if __name__ == "__main__":
    unittest.main()
