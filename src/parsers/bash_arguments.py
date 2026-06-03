"""Bash argument parser for extracting arguments from function calls."""

import shlex
from typing import List, Optional

from .base import ParserBase
from .token_iterators import (
    CommandsTokenIterator,
    FilterNestedEntitiesTokenIterator,
    FilterRedirectsTokenIterator,
)


class BashArgumentsParser(ParserBase):
    """Parses Bash code to extract arguments following a function call."""

    WHITESPACE_CHARS = " \t\r"
    WORDCHARS_APPENDUM = "./$*?@-_"

    def parse(self, content: "str") -> "Optional[List[str]]":
        """Extract arguments from the given Bash code string."""
        content = self._remove_line_continuations(content)

        try:
            lexer = shlex.shlex(content, posix=True, punctuation_chars=True)
            lexer.whitespace = self.WHITESPACE_CHARS
            lexer.wordchars += self.WORDCHARS_APPENDUM

            # Chain iterators:
            # 1. Group nested entities (subshells, backticks, expansions)
            token_iterator = FilterNestedEntitiesTokenIterator(list(lexer))

            # 2. Stop at command boundaries (separators, newlines)
            command_iterator = CommandsTokenIterator(token_iterator)

            # 3. Filter out redirections
            redirect_filter = FilterRedirectsTokenIterator(
                list(command_iterator))

            return list(redirect_filter)
        except Exception:
            return None

    def _remove_line_continuations(self, content: "str") -> "str":
        return content.replace("\\\n", "")
