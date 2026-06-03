"""Base class for error formatters."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from errors.base import LinterErrorBase


class FormatterBase(ABC):
    """Abstract base class for formatting linter errors."""

    @abstractmethod
    def format(self, errors: list[LinterErrorBase]) -> str:
        """Transform a list of LinterErrorBase objects into a formatted string."""
        pass
