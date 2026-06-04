"""Base class for all linter rules."""

from __future__ import annotations

import difflib
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from errors.base import LinterIssue


class Rule(ABC):
    """Abstract base class for all linter rules."""

    def __init__(self, functions: set[str], namespaces: set[str]) -> None:
        self.functions = functions
        self.namespaces = namespaces

    @abstractmethod
    def check(self, call: str, file: str, line: int, column: int) -> Optional[LinterIssue]:
        """Check if the call violates this rule."""
        pass

    def _find_longest_namespace_prefix(self, call: str) -> Optional[str]:
        """Find the longest namespace that is a prefix of the call."""
        parts = call.split(".")
        for i in range(len(parts) - 1, 0, -1):
            prefix = ".".join(parts[:i])
            if prefix in self.namespaces:
                return prefix
        return None

    def _is_immediate_child_of_namespace(self, call: str, namespace: str) -> bool:
        """Check if the call is an immediate child of the given namespace."""
        parts = call.split(".")
        return namespace == ".".join(parts[:-1])

    def _get_suggestion(self, call: str, namespace: str) -> Optional[str]:
        """Get a suggested function name for a misspelled call in a namespace."""
        possible_functions = [
            f for f in self.functions if f.startswith(namespace + ".")
        ]
        suggestions = difflib.get_close_matches(call, possible_functions, n=1)
        return str(suggestions[0]) if suggestions else None

    def _extract_invalid_namespace(self, call: str, longest_valid_prefix: str) -> str:
        """Extract the first invalid namespace part after a valid prefix."""
        parts = call.split(".")
        valid_parts_count = len(longest_valid_prefix.split("."))
        return ".".join(parts[: valid_parts_count + 1])
