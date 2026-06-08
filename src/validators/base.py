"""Base class for all linting validators."""

import abc
import difflib
from typing import TYPE_CHECKING, List, Optional, Set

if TYPE_CHECKING:
    from errors.base import LinterIssueBase


class ValidatorBase(abc.ABC):
    """Abstract base class for all linter validators."""

    def __init__(self, functions: "Set[str]", namespaces: "Set[str]") -> None:
        self.functions = functions
        self.namespaces = namespaces

    @abc.abstractmethod
    def check(
        self,
        call: str,
        filepath: str,
        line: int,
        column: int,
        args: "Optional[List[str]]" = None,
    ) -> "Optional[LinterIssueBase]":
        """Check if the given call violates this validator."""
        pass

    def _find_longest_namespace_prefix(self, call: str) -> "Optional[str]":
        parts = call.split(".")
        for i in range(len(parts) - 1, 0, -1):
            prefix = ".".join(parts[:i])
            if prefix in self.namespaces:
                return prefix
        return None

    def _is_immediate_child_of_namespace(self, call: str, namespace: str) -> "bool":
        parts = call.split(".")
        return namespace == ".".join(parts[:-1])

    def _get_suggestion(self, call: str, namespace: str) -> "Optional[str]":
        possible_functions = [
            f for f in self.functions if f.startswith(namespace + ".")
        ]
        suggestions = difflib.get_close_matches(call, possible_functions, n=1)
        return str(suggestions[0]) if suggestions else None

    def _extract_invalid_namespace(self, call: str, longest_valid_prefix: str) -> "str":
        parts = call.split(".")
        valid_parts_count = len(longest_valid_prefix.split("."))
        return ".".join(parts[: valid_parts_count + 1])
