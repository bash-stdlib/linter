"""Line iterator for discovering mock lifecycles in comments."""

import re
from typing import TYPE_CHECKING

from linter.line_iterators.base import LineIteratorBase

if TYPE_CHECKING:
    from linter.state.file_state import FileLinterState
    from linter.state.global_state import GlobalLinterState


class MockCommentDiscovery(LineIteratorBase):
    """Identifies mock creation and deletion via stdlib comments."""

    ACTION_CREATE = "create"
    ACTION_DELETE = "delete"

    MOCK_PATTERN = re.compile(
        r"#\s*stdlib\s+_mock\.({}|{}):\s*([^#\n\r]+)".format(ACTION_CREATE, ACTION_DELETE),
        re.IGNORECASE,
    )

    def process_line(self, line_content: str, line_num: int, offset: int) -> None:
        """Find mock lifecycle directives in comments."""
        for match in self.MOCK_PATTERN.finditer(line_content):
            mock_action = match.group(1).lower()
            mock_names_raw = match.group(2)
            absolute_offset = offset + match.start()

            mock_names = [n.strip() for n in mock_names_raw.split(",")]

            for mock_name in mock_names:
                if not mock_name:
                    continue
                if mock_action == self.ACTION_CREATE:
                    self.file_state.add_mock_lifecycle(mock_name, absolute_offset)
                elif mock_action == self.ACTION_DELETE:
                    self.file_state.end_mock_lifecycle(mock_name, absolute_offset)
