"""Rule STD004: Unknown namespace or function."""

from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from errors import STD004
from .base import Rule

if TYPE_CHECKING:
    from errors.base import LinterIssue


class UnknownCallRule(Rule):
    """Rule to check if a call is an unknown namespace or function."""

    def check(self, call: str, file: str, line: int, column: int) -> Optional[LinterIssue]:
        if call in self.functions or call in self.namespaces:
            return None

        longest_namespace = self._find_longest_namespace_prefix(call)
        if not longest_namespace:
            return STD004(file, line, column, call)

        return None
