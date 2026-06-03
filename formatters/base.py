"""Base class for issue formatters."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from errors.base import LinterIssue


class Formatter(ABC):
    """Abstract base class for formatting linter issues."""

    @abstractmethod
    def format(self, issues: list[LinterIssue]) -> str:
        """Transform a list of LinterIssue objects into a formatted string."""
        pass
