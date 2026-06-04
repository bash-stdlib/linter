"""Rule STD003: Namespace called as a function."""

from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from errors import STD003
from .base import Rule

if TYPE_CHECKING:
    from errors.base import LinterIssue


class NamespaceAsFunctionRule(Rule):
    """Rule to check if a namespace is called as a function."""

    def check(self, call: str, file: str, line: int, column: int) -> Optional[LinterIssue]:
        if call in self.namespaces:
            return STD003(file, line, column, call)
        return None
