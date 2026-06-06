"""Parser for inline linter disable comments in shell scripts."""

import re
from typing import Dict, List, Set, Tuple


class CommentIgnores:
    """Parses and stores linter error codes ignored via comments."""

    IGNORE_PATTERN = re.compile(r"#\s*stdlib:\s*disable\s+([A-Z0-9,\s]+)", re.IGNORECASE)

    def __init__(self, content: str) -> None:
        # file_ignores: (code, definition_line) -> is_used
        # Maps a global error code and its definition line to its usage status.
        self.file_ignores: Dict[Tuple[str, int], bool] = {}

        # line_ignores: line_to_check -> (code, definition_line) -> is_used
        # Maps a line number to a dictionary of error codes (and their definition lines)
        # that are ignored for that specific line.
        self.line_ignores: Dict[int, Dict[Tuple[str, int], bool]] = {}

        self._parse(content)

    def is_ignored(self, code: str, line: int) -> bool:
        """Check if a specific error code is ignored for a given line."""
        code = code.upper()
        ignored = False

        # Check file-level ignores
        for (f_code, def_line), used in self.file_ignores.items():
            if f_code == code:
                self.file_ignores[(f_code, def_line)] = True
                ignored = True

        # Check line-level ignores
        if line in self.line_ignores:
            for (l_code, def_line), used in self.line_ignores[line].items():
                if l_code == code:
                    self.line_ignores[line][(l_code, def_line)] = True
                    ignored = True

        return ignored

    def get_unused_ignores(self) -> List[Tuple[str, int]]:
        """Return a list of (code, line_number) for ignores that were never used."""
        # Collect all definitions and their usage status
        all_defs: Dict[Tuple[str, int], bool] = {}

        for (code, def_line), used in self.file_ignores.items():
            all_defs[(code, def_line)] = all_defs.get((code, def_line), False) or used

        for line_defs in self.line_ignores.values():
            for (code, def_line), used in line_defs.items():
                all_defs[(code, def_line)] = all_defs.get((code, def_line), False) or used

        return sorted([k for k, v in all_defs.items() if not v], key=lambda x: x[1])

    def _parse(self, content: str) -> None:
        lines = content.splitlines()
        if not lines:
            return

        self._parse_file_ignores(lines)
        self._parse_line_ignores(lines)

    def _parse_file_ignores(self, lines: List[str]) -> None:
        start_index = 0
        if lines and lines[0].startswith("#!"):
            start_index = 1

        for i in range(start_index, len(lines)):
            line_content = lines[i]
            if not line_content.strip():
                continue

            match = self.IGNORE_PATTERN.search(line_content)
            if not match:
                break

            codes = self._extract_codes(match.group(1))
            for code in codes:
                self.file_ignores[(code, i + 1)] = False

    def _parse_line_ignores(self, lines: List[str]) -> None:
        for i, line_content in enumerate(lines):
            line_num = i + 1
            match = self.IGNORE_PATTERN.search(line_content)
            if not match:
                continue

            codes = self._extract_codes(match.group(1))
            before_match = line_content[: match.start()].strip()
            is_same_line = bool(before_match)

            for code in codes:
                if is_same_line:
                    if line_num not in self.line_ignores:
                        self.line_ignores[line_num] = {}
                    self.line_ignores[line_num][(code, line_num)] = False
                else:
                    next_line = line_num + 1
                    if next_line not in self.line_ignores:
                        self.line_ignores[next_line] = {}
                    self.line_ignores[next_line][(code, line_num)] = False

    def _extract_codes(self, codes_str: str) -> Set[str]:
        return {c.strip().upper() for c in codes_str.replace(",", " ").split()}
