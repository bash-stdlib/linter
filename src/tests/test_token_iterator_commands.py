"""Unit tests for the TokenIteratorCommands."""

import unittest
from parsers.token_iterators.token_iterator_commands import TokenIteratorCommands


class TestTokenIteratorCommands(unittest.TestCase):
    def test_iterator__no_separators__returns_all_tokens(self) -> None:
        tokens = ["arg1", "arg2", "arg3"]
        iterator = TokenIteratorCommands(tokens)

        result = list(iterator)

        self.assertEqual(result, ["arg1", "arg2", "arg3"])

    def test_iterator__semicolon__stops_at_separator(self) -> None:
        tokens = ["arg1", "arg2", ";", "next_cmd"]
        iterator = TokenIteratorCommands(tokens)

        result = list(iterator)

        self.assertEqual(result, ["arg1", "arg2"])

    def test_iterator__newline__stops_at_newline(self) -> None:
        tokens = ["arg1", "arg2", "\n", "next_line"]
        iterator = TokenIteratorCommands(tokens)

        result = list(iterator)

        self.assertEqual(result, ["arg1", "arg2"])

    def test_iterator__pipe__stops_at_separator(self) -> None:
        tokens = ["arg1", "arg2", "|", "grep"]
        iterator = TokenIteratorCommands(tokens)

        result = list(iterator)

        self.assertEqual(result, ["arg1", "arg2"])

    def test_iterator__logical_and__stops_at_separator(self) -> None:
        tokens = ["arg1", "arg2", "&&", "other"]
        iterator = TokenIteratorCommands(tokens)

        result = list(iterator)

        self.assertEqual(result, ["arg1", "arg2"])

    def test_iterator__closing_paren__stops_at_separator(self) -> None:
        tokens = ["arg1", "arg2", ")", "next"]
        iterator = TokenIteratorCommands(tokens)

        result = list(iterator)

        self.assertEqual(result, ["arg1", "arg2"])
