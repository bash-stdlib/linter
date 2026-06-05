"""Bash argument parser for extracting arguments from function calls."""

import shlex
from typing import List, Optional

from .base import ParserBase
from .bash_command_token import BashCommandTokenIterator
from .bash_redirect_filter import BashRedirectFilterIterator
from .bash_token_iterator import BashTokenIterator


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
            token_iterator = BashTokenIterator(list(lexer))

            # 2. Stop at command boundaries (separators, newlines)
            command_iterator = BashCommandTokenIterator(token_iterator)

            # 3. Filter out redirections
            redirect_filter = BashRedirectFilterIterator(list(command_iterator))

            return list(redirect_filter)
        except Exception:
            return None

    def _remove_line_continuations(self, content: "str") -> "str":
        return content.replace("\\\n", "")
