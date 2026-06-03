import unittest

from exceptions.base import BaseLinterException
from exceptions.empty_cache import EmptyCacheError


class TestExceptions(unittest.TestCase):

    def test_base_linter_exception__can_be_raised__captures_message(
            self) -> None:
        with self.assertRaises(BaseLinterException) as context:
            raise BaseLinterException("test message")

        self.assertEqual(str(context.exception), "test message")

    def test_empty_cache_error__is_subclass_of_base__correct_inheritance(
            self) -> None:
        error = EmptyCacheError()

        self.assertIsInstance(error, BaseLinterException)


if __name__ == "__main__":
    unittest.main()
