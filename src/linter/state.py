"""State object for the linter."""

from typing import Any, Dict, List, Optional, Set, Tuple


class LinterState:
    """Holds the configuration and metadata for the linter."""

    def __init__(
        self,
        metadata: Any,
        ignored_codes: Optional[List[str]] = None,
        appendum: Optional[List[str]] = None,
    ) -> None:
        # file_ignores: (code, definition_line) -> is_used
        self.file_ignores: Dict[Tuple[str, int], bool] = {}

        # line_ignores: line_to_check -> (code, definition_line) -> is_used
        self.line_ignores: Dict[int, Dict[Tuple[str, int], bool]] = {}

        self.functions: Set[str] = set(metadata["functions"].keys())
        self.namespaces: Set[str] = set(metadata["namespaces"])
        self.metadata: Dict[str, Any] = metadata["functions"]
        self.ignored_codes: Set[str] = (
            {c.upper() for c in ignored_codes} if ignored_codes else set()
        )
        self.appendum: Set[str] = set(appendum) if appendum else set()

    def is_ignored(self, code: str, line: int) -> bool:
        """Check if a specific error code is ignored for a given line."""
        code = code.upper()

        file_ignored = self._check_file_ignores(code)
        line_ignored = self._check_line_ignores(code, line)

        return file_ignored or line_ignored

    def _check_file_ignores(self, code: str) -> bool:
        """Check and mark file-level ignores."""
        ignored = False
        for f_code, def_line in self.file_ignores:
            if f_code == code:
                self.file_ignores[(f_code, def_line)] = True
                ignored = True
        return ignored

    def _check_line_ignores(self, code: str, line: int) -> bool:
        """Check and mark line-level ignores."""
        ignored = False
        if line in self.line_ignores:
            for l_code, def_line in self.line_ignores[line]:
                if l_code == code:
                    self.line_ignores[line][(l_code, def_line)] = True
                    ignored = True
        return ignored

    def get_unused_ignores(self) -> List[Tuple[str, int]]:
        """Return a list of (code, line_number) for ignores that were never used."""
        all_defs: Dict[Tuple[str, int], bool] = {}

        for (code, def_line), used in self.file_ignores.items():
            all_defs[(code, def_line)] = all_defs.get((code, def_line), False) or used

        for line_defs in self.line_ignores.values():
            for (code, def_line), used in line_defs.items():
                all_defs[(code, def_line)] = (
                    all_defs.get((code, def_line), False) or used
                )

        return sorted([k for k, v in all_defs.items() if not v], key=lambda x: x[1])
