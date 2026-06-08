"""Base class for error formatters."""

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, List

if TYPE_CHECKING:
    from errors.base import LinterIssue


class FormatterBase(ABC):
    """Abstract base class for formatting linter errors."""

    @abstractmethod
    def format(self, errors: "List[LinterIssue]") -> "str":
        """Transform a list of LinterIssue objects into a formatted string."""
        pass
