"""Discovery pipeline for the linter."""

from typing import TYPE_CHECKING, List

from linter.discovery_iterators.base import DiscoveryAction
from linter.discovery_iterators.comment import CommentDiscoveryIterator
from linter.discovery_iterators.function_scope import FunctionScopeDiscoveryIterator
from linter.token_iterators.shlex import ShlexTokenIterator

if TYPE_CHECKING:
    from linter.discovery_iterators.base import DiscoveryIteratorBase
    from linter.state.file_state import FileLinterState
    from linter.state.global_state import GlobalLinterState


class DiscoveryPipeline:
    """Manages a chain of discovery iterators."""

    def __init__(
        self,
        global_state: "GlobalLinterState",
        file_state: "FileLinterState",
    ) -> None:
        self.iterators: List["DiscoveryIteratorBase"] = [
            CommentDiscoveryIterator(global_state, file_state),
            FunctionScopeDiscoveryIterator(global_state, file_state),
        ]

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
