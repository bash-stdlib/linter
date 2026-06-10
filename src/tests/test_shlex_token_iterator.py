"""Unit tests for the ShlexTokenIterator."""

import unittest

from linter.token_iterators.enhanced_shlex import AdvancedToken
from linter.token_iterators.shlex import ShlexTokenIterator


class TestShlexTokenIterator(unittest.TestCase):
    def test_iterator__basic_tokens__returns_all_tokens(self) -> None:
        content = "arg1 'arg 2' arg3"
        iterator = ShlexTokenIterator(content)

        result = list(iterator)

        self.assertEqual(result, ["arg1", "arg 2", "arg3"])
        self.assertFalse(iterator.parsing_error)

    def test_iterator__unbalanced_quotes__sets_error_flag(self) -> None:
        content = 'arg1 "unbalanced quote'
        iterator = ShlexTokenIterator(content)

        result = list(iterator)

        self.assertEqual(result, ["arg1"])
        self.assertTrue(iterator.parsing_error)

    def test_iterator__punctuation_chars__splits_punctuation(self) -> None:
        content = "arg1;arg2"
        iterator = ShlexTokenIterator(content)

        result = list(iterator)

        self.assertEqual(result, ["arg1", ";", "arg2"])

    def test_iterator__custom_wordchars__preserves_wordchars(self) -> None:
        content = "file-with.ext path/to/file $VAR"
        iterator = ShlexTokenIterator(content)

        result = list(iterator)

        self.assertEqual(result, ["file-with.ext", "path/to/file", "$VAR"])

    def test_iterator__quoted_special_chars__marks_as_quoted(self) -> None:
        content = 'arg "|" "#"'
        iterator = ShlexTokenIterator(content)

        result = [t for t in iterator if isinstance(t, AdvancedToken)]

        self.assertEqual(len(result), 3)
        self.assertEqual(result[0], "arg")
        self.assertFalse(result[0].is_fully_quoted)

        self.assertEqual(result[1], "|")
        self.assertTrue(result[1].is_fully_quoted)

        self.assertEqual(result[2], "#")
        self.assertTrue(result[2].is_fully_quoted)

    def test_iterator__unquoted_special_chars__marks_as_unquoted_specials(self) -> None:
        content = "arg1 | arg2 # comment"
        iterator = ShlexTokenIterator(content)

        result = [t for t in iterator if isinstance(t, AdvancedToken)]

        # shlex with punctuation_chars=True and EnhancedShlex handling of #
        # result should be ['arg1', '|', 'arg2', '#', 'comment']
        self.assertEqual(len(result), 5)
        self.assertEqual(result[1], "|")
        self.assertFalse(result[1].is_fully_quoted)
        self.assertIn("|", result[1].unquoted_specials)

        self.assertEqual(result[3], "#")
        self.assertFalse(result[3].is_fully_quoted)
        self.assertIn("#", result[3].unquoted_specials)

    def test_is_at_command_position__quoted_separator__returns_false(self) -> None:
        content = 'cmd "|"'
        iterator = ShlexTokenIterator(content)

        result = iterator.is_at_command_position()

        self.assertFalse(result)

    def test_is_at_command_position__unquoted_separator__returns_true(self) -> None:
        # If we are at the beginning of the string, it is a command position.
        iterator = ShlexTokenIterator("")
        self.assertTrue(iterator.is_at_command_position())

        # If we just had a separator, it is a command position.
        iterator = ShlexTokenIterator("| ")
        self.assertTrue(iterator.is_at_command_position())


if __name__ == "__main__":
    unittest.main()
