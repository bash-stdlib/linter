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

    def parse(self, content: "str") -> "Optional[List[str]]":
        """Extract arguments from the given Bash code string."""
        content = self._remove_line_continuations(content)

        shlex_iterator = ShlexTokenIterator(content)
        nested_iterator = FilterNestedEntitiesTokenIterator(list(shlex_iterator))
        command_iterator = CommandsTokenIterator(nested_iterator)
        redirect_filter = FilterRedirectsTokenIterator(list(command_iterator))

        if shlex_iterator.parsing_error and not command_iterator.stopped_at_separator:
            return None

        return list(redirect_filter)

    def _remove_line_continuations(self, content: "str") -> "str":
        return content.replace("\\\n", "")
