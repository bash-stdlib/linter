"""Unit tests for the BashCommandTokenIterator."""

import unittest
from parsers.bash_command_token import BashCommandTokenIterator


class TestBashCommandTokenIterator(unittest.TestCase):
    def test_iterator__no_separators__returns_all_tokens(self) -> None:
        tokens = ["arg1", "arg2", "arg3"]
        iterator = BashCommandTokenIterator(tokens)

        result = list(iterator)

        self.assertEqual(result, ["arg1", "arg2", "arg3"])

    def test_iterator__semicolon__stops_at_separator(self) -> None:
        tokens = ["arg1", "arg2", ";", "next_cmd"]
        iterator = BashCommandTokenIterator(tokens)

        result = list(iterator)

        self.assertEqual(result, ["arg1", "arg2"])

    def test_iterator__newline__stops_at_newline(self) -> None:
        tokens = ["arg1", "arg2", "\n", "next_line"]
        iterator = BashCommandTokenIterator(tokens)

        result = list(iterator)

        self.assertEqual(result, ["arg1", "arg2"])

    def test_iterator__pipe__stops_at_separator(self) -> None:
        tokens = ["arg1", "arg2", "|", "grep"]
        iterator = BashCommandTokenIterator(tokens)

        result = list(iterator)

        self.assertEqual(result, ["arg1", "arg2"])

    def test_iterator__logical_and__stops_at_separator(self) -> None:
        tokens = ["arg1", "arg2", "&&", "other"]
        iterator = BashCommandTokenIterator(tokens)

        result = list(iterator)

        self.assertEqual(result, ["arg1", "arg2"])

    def test_iterator__closing_paren__stops_at_separator(self) -> None:
        tokens = ["arg1", "arg2", ")", "next"]
        iterator = BashCommandTokenIterator(tokens)

        result = list(iterator)

        self.assertEqual(result, ["arg1", "arg2"])
