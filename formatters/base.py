"""Base class for issue formatters."""

from abc import ABC, abstractmethod


class Formatter(ABC):
    """Abstract base class for formatting linter issues."""

    @abstractmethod
    def format(self, issues):
        """Transform a list of LinterIssue objects into a formatted string."""
        pass
