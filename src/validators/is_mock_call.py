"""Validator for mock-related calls."""

import re
from typing import TYPE_CHECKING, List, Optional, Set

from issues import STD007, STD010, STD002
from validators.base import ValidatorBase

if TYPE_CHECKING:
    from issues.base import LinterIssueBase
    from linter.state.file_state import FileLinterState
    from linter.state.global_state import GlobalLinterState


class IsMockCallValidator(ValidatorBase):
    """Validates calls to mock objects and ensures they are used in test files."""

    MOCK_TOKEN = ".mock."
    MOCK_PREFIX = "_mock."
    MOCK_META_PREFIX = "object.mock."

    def __init__(
        self, global_state: "GlobalLinterState", file_state: "FileLinterState"
    ) -> None:
        super().__init__(global_state, file_state)
        self.mock_methods: Set[str] = self._derive_mock_methods()

    def _derive_mock_methods(self) -> Set[str]:
        """Derive mock methods from metadata by looking for 'object.mock.*'."""
        methods = set()
        for func_name in self.global_state.functions:
            if func_name.startswith(self.MOCK_META_PREFIX):
                method = func_name[len(self.MOCK_META_PREFIX):]
                methods.add(method)
        return methods

    def check(
        self,
        call: str,
        filepath: str,
        line: int,
        column: int,
        args: "Optional[List[str]]" = None,
        offset: int = 0,
    ) -> "Optional[LinterIssueBase]":
        is_test_file = "test" in filepath.lower()

        if self._is_mock_system_call(call):
             if not is_test_file:
                 return STD007(filepath, line, column, call)
             return None

        if self.MOCK_TOKEN in call:
            return self._validate_mock_object_call(call, filepath, line, column, offset, is_test_file)

        if self.file_state.is_mock_active(call, offset):
            if not is_test_file:
                 return STD007(filepath, line, column, call)
            return None

        return None

    def _is_mock_system_call(self, call: str) -> bool:
        return call.startswith(self.MOCK_PREFIX)

    def _validate_mock_object_call(
        self, call: str, filepath: str, line: int, column: int, offset: int, is_test_file: bool
    ) -> "Optional[LinterIssueBase]":
        parts = call.split(self.MOCK_TOKEN, 1)
        mock_name = parts[0]
        method = parts[1]

        if not is_test_file:
             return STD007(filepath, line, column, call)

        if not self.file_state.is_mock_active(mock_name, offset):
            return STD010(
                filepath, line, column, mock_name,
                "Mock '{}' is not active at this position.".format(mock_name)
            )

        if method not in self.mock_methods:
            return STD002(filepath, line, column, call, "{}{}".format(mock_name, self.MOCK_TOKEN[:-1]))

        return None
