"""Base class for linter line iterators."""

import abc
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from linter.state import LinterState


class LineIteratorBase(abc.ABC):
    """Abstract base class for iterators that process script lines."""

    def __init__(self, state: "LinterState") -> None:
        self.state = state

    @abc.abstractmethod
    def process_line(self, line_content: str, line_num: int) -> None:
        """Process a single line and update the linter state."""
        pass
