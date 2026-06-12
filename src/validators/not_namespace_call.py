"""Linter validator to ensure namespaces are not called as functions."""

from typing import TYPE_CHECKING, List, Optional

from issues import STD003
from validators.base import ValidatorBase

if TYPE_CHECKING:
    from issues.base import LinterIssueBase


class NotNamespaceCallValidator(ValidatorBase):
    """Checks if a namespace is being called as a function."""

    def check(
        self,
        call: str,
        filepath: str,
        line: int,
        column: int,
        args: "Optional[List[str]]" = None,
        offset: int = 0,
    ) -> "Optional[LinterIssueBase]":
        if (
            call in self.global_state.namespaces
            or call in self.global_state.extra_namespaces
        ):
            return STD003(filepath, line, column, call)
        return None
