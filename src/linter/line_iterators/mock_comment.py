"""Line iterator for discovering mock lifecycles in comments."""

import re
from typing import TYPE_CHECKING

from linter.line_iterators.base import LineIteratorBase

if TYPE_CHECKING:
    from linter.state.file_state import FileLinterState
    from linter.state.global_state import GlobalLinterState


class MockCommentDiscovery(LineIteratorBase):
    """Identifies mock creation and deletion via stdlib comments."""

    MOCK_PATTERN = re.compile(
        r"#\s*stdlib\s+_mock\.(create|delete):\s*([^#\n\r]+)", re.IGNORECASE
    )

    def process_line(self, line_content: str, line_num: int, offset: int) -> None:
        """Find mock lifecycle directives in comments."""
        for match in self.MOCK_PATTERN.finditer(line_content):
            action = match.group(1).lower()
            names_raw = match.group(2)
            absolute_offset = offset + match.start()

            names = [n.strip() for n in names_raw.split(",")]

            for name in names:
                if not name:
                    continue
                if action == "create":
                    self.file_state.add_mock_lifecycle(name, absolute_offset)
                elif action == "delete":
                    self.file_state.end_mock_lifecycle(name, absolute_offset)
