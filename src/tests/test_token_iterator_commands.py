"""Unit tests for the CommandsTokenIterator."""

import unittest

from parsers.token_iterators.commands import CommandsTokenIterator


class TestCommandsTokenIterator(unittest.TestCase):
    def test_iterator__no_separators__returns_all_tokens(self) -> None:
        tokens = ["arg1", "arg2", "arg3"]
        iterator = CommandsTokenIterator(tokens)

        result = list(iterator)

        self.assertEqual(result, ["arg1", "arg2", "arg3"])

    def test_iterator__semicolon__stops_at_separator(self) -> None:
        tokens = ["arg1", "arg2", ";", "next_cmd"]
        iterator = CommandsTokenIterator(tokens)

        result = list(iterator)

        self.assertEqual(result, ["arg1", "arg2"])

    def test_iterator__no_separators__stopped_at_separator_is_false(self) -> None:
        tokens = ["arg1", "arg2"]
        iterator = CommandsTokenIterator(tokens)

        list(iterator)

        self.assertFalse(iterator.stopped_at_separator)

    def test_iterator__with_separator__stopped_at_separator_is_true(self) -> None:
        tokens = ["arg1", ";", "arg2"]
        iterator = CommandsTokenIterator(tokens)

        list(iterator)

        self.assertTrue(iterator.stopped_at_separator)

    def test_iterator__with_newline__stopped_at_separator_is_true(self) -> None:
        tokens = ["arg1", "\n", "arg2"]
        iterator = CommandsTokenIterator(tokens)

        list(iterator)

        self.assertTrue(iterator.stopped_at_separator)

    def test_iterator__newline__stops_at_newline(self) -> None:
        tokens = ["arg1", "arg2", "\n", "next_line"]
        iterator = CommandsTokenIterator(tokens)

        result = list(iterator)

        self.assertEqual(result, ["arg1", "arg2"])

    def test_iterator__pipe__stops_at_separator(self) -> None:
        tokens = ["arg1", "arg2", "|", "grep"]
        iterator = CommandsTokenIterator(tokens)

        result = list(iterator)

        self.assertEqual(result, ["arg1", "arg2"])

    def test_iterator__logical_and__stops_at_separator(self) -> None:
        tokens = ["arg1", "arg2", "&&", "other"]
        iterator = CommandsTokenIterator(tokens)

        result = list(iterator)

        self.assertEqual(result, ["arg1", "arg2"])

    def test_iterator__closing_paren__stops_at_separator(self) -> None:
        tokens = ["arg1", "arg2", ")", "next"]
        iterator = CommandsTokenIterator(tokens)

        result = list(iterator)

        self.assertEqual(result, ["arg1", "arg2"])

if __name__ == "__main__":
    unittest.main()
