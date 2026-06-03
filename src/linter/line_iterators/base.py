"""Base class for linter line iterators."""

import abc
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from linter.state.file_state import FileLinterState
    from linter.state.global_state import GlobalLinterState


class LineIteratorBase(abc.ABC):
    """Abstract base class for iterators that process script lines."""

    def __init__(
        self, global_state: "GlobalLinterState", file_state: "FileLinterState"
    ) -> None:
        self.global_state = global_state
        self.file_state = file_state

    @abc.abstractmethod
    def process_line(self, line_content: str, line_num: int, offset: int) -> None:
        """Process a single line and update the linter state."""
        pass
