"""Base class for linter events."""

import abc
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from linter.state.file_state import FileLinterState
    from linter.state.global_state import GlobalLinterState


class EventBase(abc.ABC):
    """Abstract base class for code events."""

    def __init__(
        self, global_state: "GlobalLinterState", file_state: "FileLinterState"
    ) -> None:
        self.global_state = global_state
        self.file_state = file_state

    @abc.abstractmethod
    def match(self, line_content: str) -> bool:
        """Check if the line content matches the event."""
        pass

    @abc.abstractmethod
    def handle(self, line_content: str, line_num: int, offset: int) -> None:
        """Handle the event and update the linter state."""
        pass
