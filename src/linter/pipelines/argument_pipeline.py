"""Argument pipeline for extracting arguments from function calls."""

from typing import List, Optional

from linter.token_iterators import (
    CommandsTokenIterator,
    FilterNestedEntitiesTokenIterator,
    FilterRedirectsTokenIterator,
    ShlexTokenIterator,
)
from linter.transformers import ExpansionTransformer, LineContinuationTransformer


class ArgumentPipeline:
    """Manages the extraction of arguments from Bash code."""

    def __init__(self) -> None:
        self.line_transformer = LineContinuationTransformer()
        self.expansion_transformer = ExpansionTransformer()

    def run(self, content: str) -> Optional[List[str]]:
        """Extract arguments from the given Bash code string."""
        content = self.line_transformer.transform(content)
        content = self.expansion_transformer.transform(content)

        shlex_iterator = ShlexTokenIterator(content)
        nested_iterator = FilterNestedEntitiesTokenIterator(shlex_iterator)
        command_iterator = CommandsTokenIterator(nested_iterator)
        redirect_filter = FilterRedirectsTokenIterator(command_iterator)

        arguments = [str(arg) for arg in redirect_filter]

        if shlex_iterator.parsing_error and not command_iterator.stopped_at_separator:
            return None

        return arguments
