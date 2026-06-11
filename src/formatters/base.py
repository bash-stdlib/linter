"""Base class for issue formatters."""

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, List

if TYPE_CHECKING:
    from issues.base import LinterIssueBase


class FormatterBase(ABC):
    """Abstract base class for formatting linter issues."""

    @abstractmethod
    def format(self, issues: "List[LinterIssueBase]") -> "str":
        """Transform a list of LinterIssueBase objects into a formatted string."""
        pass
