"""Bash argument parser for extracting arguments from function calls."""

import shlex
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

    def parse(self, content: "str") -> "Optional[List[str]]":
        """Extract arguments from the given Bash code string."""
        content = self._remove_line_continuations(content)

        # 1. Tokenize using shlex
        shlex_iterator = ShlexTokenIterator(content)

        # 2. Group nested entities (subshells, backticks, expansions)
        # FilterNestedEntitiesTokenIterator expects a list because it needs random access
        # for lookahead.
        tokens = list(shlex_iterator)
        nested_iterator = FilterNestedEntitiesTokenIterator(tokens)

        # 3. Stop at command boundaries (separators, newlines)
        command_iterator = CommandsTokenIterator(nested_iterator)

        # 4. Filter out redirections
        # FilterRedirectsTokenIterator also expects a list.
        tokens_in_command = list(command_iterator)
        redirect_filter = FilterRedirectsTokenIterator(tokens_in_command)

        # Check for parsing errors (e.g. unbalanced quotes)
        # We only consider it an error if it happened before a command terminator.
        if shlex_iterator.parsing_error and not command_iterator.stopped_at_separator:
            return None

        return list(redirect_filter)

    def _remove_line_continuations(self, content: "str") -> "str":
        return content.replace("\\\n", "")
