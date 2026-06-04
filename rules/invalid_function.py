"""Rule STD002: Invalid function name in valid namespace."""

from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from errors import STD002
from .base import Rule

if TYPE_CHECKING:
    from errors.base import LinterIssue


class InvalidFunctionRule(Rule):
    """Rule to check if a function name is invalid but the namespace is valid."""

    def check(self, call: str, file: str, line: int, column: int) -> Optional[LinterIssue]:
        if call in self.functions or call in self.namespaces:
            return None

        longest_namespace = self._find_longest_namespace_prefix(call)
        if longest_namespace and self._is_immediate_child_of_namespace(
            call, longest_namespace
        ):
            suggestion = self._get_suggestion(call, longest_namespace)
            return STD002(file, line, column, call, longest_namespace, suggestion)

        return None
