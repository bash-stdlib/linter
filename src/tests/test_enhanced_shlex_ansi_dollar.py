"""Tests for EnhancedShlex ANSI-C and Dollar quoting."""

import unittest
from linter.enhanced_shlex import EnhancedShlex

class TestEnhancedShlexAnsiDollarQuotes(unittest.TestCase):
    """Tests for Bash-specific ANSI-C and Dollar quoting."""

    def test_read_token__ansi_c_quoted__correct_offsets_and_quoting(self) -> None:
        # Note: shlex with posix=True splits $'...' into '$' and '...' unless $ is in wordchars
        # In ShlexTokenIterator, $ is in wordchars.
        content = "$'hello\\nworld'"
        # Simulate ShlexTokenIterator settings
        lexer = EnhancedShlex(content, posix=True)
        lexer.wordchars += "$"

        result = next(lexer)

        self.assertEqual(result, "$hello\\nworld")
        self.assertEqual(result.start_offset, 0)
        self.assertEqual(result.end_offset, 15)
        self.assertTrue(result.is_fully_quoted)
        self.assertEqual(content[result.start_offset:result.end_offset], "$'hello\\nworld'")

    def test_read_token__dollar_quoted__correct_offsets_and_quoting(self) -> None:
        content = ' $"hello"'
        lexer = EnhancedShlex(content, posix=True)
        lexer.wordchars += "$"

        result = next(lexer)

        self.assertEqual(result, "$hello")
        self.assertEqual(result.start_offset, 1)
        self.assertEqual(result.end_offset, 9)
        self.assertTrue(result.is_fully_quoted)
        self.assertEqual(content[result.start_offset:result.end_offset], '$"hello"')

    def test_read_token__nested_ansi_c_in_expansion__correctly_reconstructed(self) -> None:
        # This is the case reported by the user
        content = '"${var/$\'\\n\'/ }"'
        lexer = EnhancedShlex(content, posix=True)

        result = next(lexer)

        self.assertEqual(result, "${var/$'\\n'/ }")
        self.assertTrue(result.is_fully_quoted)
        self.assertEqual(result.start_offset, 0)
        self.assertEqual(result.end_offset, 16)

    def test_read_token__punctuation_followed_by_quote__splits_correctly(self) -> None:
        content = 'VAR="${var}"'
        # explicitly use '=' as punctuation to force split
        lexer = EnhancedShlex(content, posix=True, target_chars=['='], punctuation_chars='=')

        tokens = list(lexer)

        # shlex splits at '=' because punctuation_chars='='
        # EnhancedShlex should NOT merge VAR= and "${var}"
        self.assertEqual(tokens[0], "VAR")
        self.assertEqual(tokens[1], "=")
        self.assertEqual(tokens[2], "${var}")
        self.assertEqual(tokens[0].end_offset, 3)
        self.assertEqual(tokens[1].start_offset, 3)
        self.assertEqual(tokens[1].end_offset, 4)
        self.assertEqual(tokens[2].start_offset, 4)

    def test_read_token__ansi_c_no_wordchars_dollar__splits_correctly(self) -> None:
        content = "$'foo'"
        lexer = EnhancedShlex(content, posix=True)
        # $ NOT in wordchars, so shlex returns '$' then 'foo'

        tokens = list(lexer)
        self.assertEqual(len(tokens), 2)
        self.assertEqual(tokens[0], "$")
        self.assertEqual(tokens[1], "foo")
        self.assertEqual(content[tokens[0].start_offset:tokens[0].end_offset], "$")
        self.assertEqual(content[tokens[1].start_offset:tokens[1].end_offset], "'foo'")

if __name__ == "__main__":
    unittest.main()
