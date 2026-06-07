"""Bash argument parser for extracting arguments from function calls."""

from typing import List, Optional

from .base import ParserBase
from .token_iterators import (
    CommandsTokenIterator,
    FilterNestedEntitiesTokenIterator,
    FilterRedirectsTokenIterator,
    ShlexTokenIterator,
    CommentsFilterTokenIterator,
)
from parsers.transformers import ExpansionTransformer, LineContinuationTransformer


class BashArgumentsParser(ParserBase):
    """Parses Bash code to extract arguments following a function call."""

    def __init__(self) -> None:
        self.line_transformer = LineContinuationTransformer()
        self.expansion_transformer = ExpansionTransformer()

    def parse(self, content: "str") -> "Optional[List[str]]":
        """Extract arguments from the given Bash code string."""
        content = self.line_transformer.transform(content)
        content = self.expansion_transformer.transform(content)

        shlex_iterator = ShlexTokenIterator(content)
        comments_iterator = CommentsFilterTokenIterator(shlex_iterator)
        nested_iterator = FilterNestedEntitiesTokenIterator(comments_iterator)
        command_iterator = CommandsTokenIterator(nested_iterator)
        redirect_filter = FilterRedirectsTokenIterator(command_iterator)

        arguments = list(redirect_filter)

        if shlex_iterator.parsing_error and not command_iterator.stopped_at_separator:
            return None

        return arguments
