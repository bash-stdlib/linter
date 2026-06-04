"""Base class for all linting rules."""

from __future__ import annotations

import abc
import difflib
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from errors.base import LinterIssue


class Rule(abc.ABC):
    """Abstract base class for all linter rules."""

    def __init__(self, functions: set[str], namespaces: set[str]) -> None:
        self.functions = functions
        self.namespaces = namespaces

    @abc.abstractmethod
    def check(
        self, call: str, file: str, line: int, column: int
    ) -> Optional[LinterIssue]:
        """Check if the given call violates this rule."""
        pass

    def _find_longest_namespace_prefix(self, call: str) -> Optional[str]:
        parts = call.split(".")
        for i in range(len(parts) - 1, 0, -1):
            prefix = ".".join(parts[:i])
            if prefix in self.namespaces:
                return prefix
        return None

    def _is_immediate_child_of_namespace(self, call: str, namespace: str) -> bool:
        parts = call.split(".")
        return namespace == ".".join(parts[:-1])

    def _get_suggestion(self, call: str, namespace: str) -> Optional[str]:
        possible_functions = [
            f for f in self.functions if f.startswith(namespace + ".")
        ]
        suggestions = difflib.get_close_matches(call, possible_functions, n=1)
        return str(suggestions[0]) if suggestions else None

    def _extract_invalid_namespace(self, call: str, longest_valid_prefix: str) -> str:
        parts = call.split(".")
        valid_parts_count = len(longest_valid_prefix.split("."))
        return ".".join(parts[: valid_parts_count + 1])
