"""Parser for inline linter disable comments in shell scripts."""

import re
from typing import Dict, Set


class CommentIgnores:
    """Parses and stores linter error codes ignored via comments."""

    IGNORE_PATTERN = re.compile(r"#\s*stdlib:\s*disable\s+([A-Z0-9,\s]+)", re.IGNORECASE)

    def __init__(self, content: str) -> None:
        self.file_ignores: Set[str] = set()
        self.line_ignores: Dict[int, Set[str]] = {}
        self._parse(content)

    def is_ignored(self, code: str, line: int) -> bool:
        """Check if a specific error code is ignored for a given line."""
        code = code.upper()
        if code in self.file_ignores:
            return True
        if line in self.line_ignores and code in self.line_ignores[line]:
            return True
        return False

    def _parse(self, content: str) -> None:
        lines = content.splitlines()
        if not lines:
            return

        # Check for file-level ignores at the top
        start_index = 0
        if lines[0].startswith("#!"):
            start_index = 1

        for i in range(start_index, len(lines)):
            line_content = lines[i]
            if not line_content.strip():
                continue

            match = self.IGNORE_PATTERN.search(line_content)
            if not match:
                break

            codes = self._extract_codes(match.group(1))
            self.file_ignores.update(codes)

        # Parse all lines for line-level ignores
        for i, line_content in enumerate(lines):
            line_num = i + 1
            match = self.IGNORE_PATTERN.search(line_content)
            if not match:
                continue

            codes = self._extract_codes(match.group(1))

            # Same line ignore
            if line_num not in self.line_ignores:
                self.line_ignores[line_num] = set()
            self.line_ignores[line_num].update(codes)

            # Next line ignore
            next_line = line_num + 1
            if next_line not in self.line_ignores:
                self.line_ignores[next_line] = set()
            self.line_ignores[next_line].update(codes)

    def _extract_codes(self, codes_str: str) -> Set[str]:
        return {c.strip().upper() for c in codes_str.replace(",", " ").split()}
