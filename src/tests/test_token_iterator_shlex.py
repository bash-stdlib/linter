"""Unit tests for the ShlexTokenIterator."""

import unittest

from parsers.token_iterators.shlex import ShlexTokenIterator


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
