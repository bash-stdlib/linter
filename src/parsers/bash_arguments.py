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

            tokens = []
            parsing_error = False
            try:
                while True:
                    token = lexer.get_token()
                    if not token:
                        break
                    tokens.append(token)
            except ValueError:
                # shlex raises ValueError for unbalanced quotes
                parsing_error = True

            # Chain iterators:
            # 1. Group nested entities (subshells, backticks, expansions)
            token_iterator = FilterNestedEntitiesTokenIterator(tokens)

            # 2. Stop at command boundaries (separators, newlines)
            # We track if we stopped because of a separator
            command_iterator = CommandsTokenIterator(token_iterator)
            args_tokens = []
            stopped_at_separator = False
            for token in command_iterator:
                args_tokens.append(token)

            # Check if the iterator stopped because it saw a separator or reached the end
            if command_iterator.stopped_at_separator:
                stopped_at_separator = True

            # If shlex failed but we already reached a command separator,
            # we can safely ignore the error as it likely belongs to the next command/outer context.
            if parsing_error and not stopped_at_separator:
                return None

            # 3. Filter out redirections
            redirect_filter = FilterRedirectsTokenIterator(args_tokens)

            return list(redirect_filter)
        except Exception:
            return None

    def _remove_line_continuations(self, content: "str") -> "str":
        return content.replace("\\\n", "")
