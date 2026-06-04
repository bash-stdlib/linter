"""Base class for error formatters."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from errors.base import LinterError


class Formatter(ABC):
    """Abstract base class for formatting linter errors."""

    @abstractmethod
    def format(self, errors: list[LinterError]) -> str:
        """Transform a list of LinterError objects into a formatted string."""
        pass
