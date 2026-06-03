"""ValidatorBase to prevent calling namespaces directly."""

from typing import TYPE_CHECKING, List, Optional

from issues import STD003
from validators.base import ValidatorBase

if TYPE_CHECKING:
    from issues.base import LinterIssueBase


class NotNamespaceCallValidator(ValidatorBase):
    """Checks if the call is actually a namespace, which is not allowed."""

    def check(
        self,
        call: str,
        filepath: str,
        line: int,
        column: int,
        args: "Optional[List[str]]" = None,
    ) -> "Optional[LinterIssueBase]":
        if (
            call in self.global_state.namespaces
            and call not in self.global_state.functions
        ):
            return STD003(filepath, line, column, call)
        return None
