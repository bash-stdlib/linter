"""Parser for inline linter disable comments in shell scripts."""

import re
from typing import TYPE_CHECKING, Set

from linter.line_iterators.base import LineIteratorBase

if TYPE_CHECKING:
    from linter.state.file_state import FileLinterState
    from linter.state.global_state import GlobalLinterState


class CommentIgnores(LineIteratorBase):
    """Parses and stores linter issue codes ignored via comments."""

    IGNORE_PATTERN = re.compile(
        r"#\s*stdlib:\s*disable\s+([A-Z0-9,\s]+)", re.IGNORECASE
    )

    def __init__(
        self,
        global_state: "GlobalLinterState",
        file_state: "FileLinterState",
    ) -> None:
        super().__init__(global_state, file_state)
        self._in_header = True

    def process_line(self, line_content: str, line_num: int, offset: int) -> None:
        """Process a single line to extract ignore directives."""
        if self._in_header:
            if line_num == 1 and line_content.startswith("#!"):
                return
            if not line_content.strip():
                return

        match = self.IGNORE_PATTERN.search(line_content)
        if not match:
            if self._in_header:
                self._in_header = False
            return

        codes = self._extract_codes(match.group(1))

        if self._in_header:
            for code in codes:
                self.file_state.file_ignores[(code, line_num)] = False
        else:
            before_match = line_content[: match.start()].strip()
            is_same_line = bool(before_match)

            for code in codes:
                if is_same_line:
                    if line_num not in self.file_state.line_ignores:
                        self.file_state.line_ignores[line_num] = {}
                    self.file_state.line_ignores[line_num][(code, line_num)] = False
                else:
                    next_line = line_num + 1
                    if next_line not in self.file_state.line_ignores:
                        self.file_state.line_ignores[next_line] = {}
                    self.file_state.line_ignores[next_line][(code, line_num)] = False

    def _extract_codes(self, codes_str: str) -> Set[str]:
        return {c.strip().upper() for c in codes_str.replace(",", " ").split()}
