"""Rule STD001: Invalid namespace."""

from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from errors import STD001
from .base import Rule

if TYPE_CHECKING:
    from errors.base import LinterIssue


class InvalidNamespaceRule(Rule):
    """Rule to check if a namespace is invalid."""

    def check(self, call: str, file: str, line: int, column: int) -> Optional[LinterIssue]:
        if call in self.functions or call in self.namespaces:
            return None

        longest_namespace = self._find_longest_namespace_prefix(call)
        if longest_namespace and not self._is_immediate_child_of_namespace(
            call, longest_namespace
        ):
            invalid_namespace = self._extract_invalid_namespace(call, longest_namespace)
            return STD001(file, line, column, call, invalid_namespace)

        return None
