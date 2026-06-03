"""Discovery pipeline for the linter."""

from typing import TYPE_CHECKING, List

from linter.discovery_iterators import (
    CommentDiscoveryIterator,
    DiscoveryAction,
    DiscoveryIteratorBase,
    FunctionScopeDiscoveryIterator,
)
from linter.pipelines.base import BasePipeline
from linter.token_iterators.shlex import ShlexTokenIterator

if TYPE_CHECKING:
    from linter.state.file_state import FileLinterState
    from linter.state.global_state import GlobalLinterState


class DiscoveryPipeline(BasePipeline):
    """Manages a chain of discovery iterators."""

    def __init__(
        self,
        global_state: "GlobalLinterState",
        file_state: "FileLinterState",
    ) -> None:
        super().__init__(global_state, file_state)
        self.iterators: List["DiscoveryIteratorBase"] = [
            CommentDiscoveryIterator(global_state, file_state),
            FunctionScopeDiscoveryIterator(global_state, file_state),
        ]

    def execute(self) -> None:
        """Execute the pipeline (abstract method from BasePipeline)."""
        pass

    def process(self, content: str) -> None:
        """Stream tokens through all discovery iterators."""
        tokens = ShlexTokenIterator(content)
        try:
            for token in tokens:
                for iterator in self.iterators:
                    action = iterator.handle_token(token)
                    if action == DiscoveryAction.STOP_TOKEN:
                        break
                    if action == DiscoveryAction.STOP_LINE:
                        tokens.skip_to_newline()
                        break
        except ValueError:
            pass
