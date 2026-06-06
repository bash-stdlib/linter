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

    ShlexTokenIterator = ShlexTokenIterator

    def parse(self, content: "str") -> "Optional[List[str]]":
        """Extract arguments from the given Bash code string."""
        content = self._remove_line_continuations(content)
        content = self._simplify_expansions(content)

        shlex_iterator = ShlexTokenIterator(content)
        nested_iterator = FilterNestedEntitiesTokenIterator(shlex_iterator)
        command_iterator = CommandsTokenIterator(nested_iterator)
        redirect_filter = FilterRedirectsTokenIterator(command_iterator)

        arguments = list(redirect_filter)

        if shlex_iterator.parsing_error and not command_iterator.stopped_at_separator:
            return None

        return arguments

    def _remove_line_continuations(self, content: "str") -> "str":
        return content.replace("\\\n", "")

    def _simplify_expansions(self, content: "str") -> "str":
        import re

        # Simplify $(( ... )) to $((X)) non-greedily
        content = re.sub(r"\$\(\(.*?\)\)", "$((X))", content)

        # Simplify ${ ... } to ${X}
        content = re.sub(r"\${[^}]*}", "${X}", content)

        return content
