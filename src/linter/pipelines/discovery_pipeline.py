"""Discovery pipeline for the linter."""

from typing import TYPE_CHECKING, List

from linter.discovery_iterators import (
    CommentDiscoveryIterator,
    DiscoveryAction,
    DiscoveryIteratorBase,
    FunctionScopeDiscoveryIterator,
    MockDiscoveryIterator,
)
from linter.line_iterators import CommentIgnores, LineIteratorBase, MockCommentDiscovery
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
            MockDiscoveryIterator(global_state, file_state),
        ]
        self.line_iterators: List["LineIteratorBase"] = [
            CommentIgnores(global_state, file_state),
            MockCommentDiscovery(global_state, file_state),
        ]

    def execute(self) -> None:
        """Execute the pipeline (abstract method from BasePipeline)."""
        pass

    def process(self, content: str) -> None:
        """Process content through line and token discovery iterators."""
        self._run_line_discovery(content)
        self._run_token_discovery(content)

    def _run_line_discovery(self, content: str) -> None:
        """Perform line-based discovery pass."""
        offset = 0
        for i, line_content in enumerate(content.splitlines(True)):
            line_num = i + 1
            for iterator in self.line_iterators:
                iterator.process_line(line_content, line_num, offset)
            offset += len(line_content)

    def _run_token_discovery(self, content: str) -> None:
        """Perform token-based discovery pass."""
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
