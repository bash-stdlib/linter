"""Line iterator that manages and dispatches code events."""

from typing import TYPE_CHECKING, List

from linter.line_iterators.base import LineIteratorBase
from linter.line_iterators.events.function import FunctionEvent

if TYPE_CHECKING:
    from linter.line_iterators.events.base import EventBase
    from linter.state.file_state import FileLinterState
    from linter.state.global_state import GlobalLinterState


class EventsIterator(LineIteratorBase):
    """Line iterator that delegates to a list of event handlers."""

    def __init__(
        self, global_state: "GlobalLinterState", file_state: "FileLinterState"
    ) -> None:
        super().__init__(global_state, file_state)
        self.events: List["EventBase"] = [
            FunctionEvent(global_state, file_state),
        ]

    def process_line(self, line_content: str, line_num: int, offset: int) -> None:
        """Process a line by dispatching to matching events."""
        for event in self.events:
            if event.match(line_content):
                event.handle(line_content, line_num, offset)
