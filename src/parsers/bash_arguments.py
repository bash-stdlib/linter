"""Bash argument parser for extracting arguments from function calls."""

from typing import List, Optional

from .base import ParserBase
from .token_iterators import (
    CommandsTokenIterator,
    FilterNestedEntitiesTokenIterator,
    FilterRedirectsTokenIterator,
    ShlexTokenIterator,
)


class BashArgumentsParser(ParserBase):
    """Parses Bash code to extract arguments following a function call."""

    WHITESPACE_CHARS = " \t\r"
    WORDCHARS_APPENDUM = "./$*?@-_"

    def parse(self, content: "str") -> "Optional[List[str]]":
        """Extract arguments from the given Bash code string."""
        content = self._remove_line_continuations(content)

        try:
            # 1. Tokenize using shlex
            shlex_iterator = ShlexTokenIterator(content, self.WHITESPACE_CHARS,
                                                self.WORDCHARS_APPENDUM)

            # 2. Group nested entities (subshells, backticks, expansions)
            nested_entities_iterator = FilterNestedEntitiesTokenIterator(
                list(shlex_iterator))

            # 3. Stop at command boundaries (separators, newlines)
            command_iterator = CommandsTokenIterator(nested_entities_iterator)
            args_tokens = []
            for token in command_iterator:
                args_tokens.append(token)

            # If shlex failed but we haven't reached a command separator,
            # it means the parsing error is within our arguments.
            if (shlex_iterator.parsing_error
                    and not command_iterator.stopped_at_separator):
                return None

            # 4. Filter out redirections
            redirect_filter = FilterRedirectsTokenIterator(args_tokens)

            return list(redirect_filter)
        except Exception:
            return None

    def _remove_line_continuations(self, content: "str") -> "str":
        return content.replace("\\\n", "")
