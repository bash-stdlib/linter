"""Validator for mock-related calls."""

import re
from typing import TYPE_CHECKING, List, Optional, Set

from issues.errors.STD007 import STD007
from issues.errors.STD010 import STD010
from issues.errors.STD002 import STD002
from validators.base import ValidatorBase

if TYPE_CHECKING:
    from issues.base import LinterIssueBase
    from linter.state.file_state import FileLinterState
    from linter.state.global_state import GlobalLinterState


class IsMockCallValidator(ValidatorBase):
    """Validates calls to mock objects and ensures they are used in test files."""

    def __init__(
        self, global_state: "GlobalLinterState", file_state: "FileLinterState"
    ) -> None:
        super().__init__(global_state, file_state)
        self.mock_methods: Set[str] = self._derive_mock_methods()

    def _derive_mock_methods(self) -> Set[str]:
        """Derive mock methods from metadata by looking for 'object.mock.*'."""
        methods = set()
        for func_name in self.global_state.functions:
            if func_name.startswith("object.mock."):
                method = func_name[len("object.mock."):]
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

        # Check for _mock.* calls
        if call.startswith("_mock."):
             if not is_test_file:
                 return STD007(filepath, line, column, call)
             return None

        # Check for <name>.mock.* calls
        if ".mock." in call:
            parts = call.split(".mock.", 1)
            mock_name = parts[0]
            method = parts[1]

            if not is_test_file:
                 return STD007(filepath, line, column, call)

            # Check if mock is active
            if not self.file_state.is_mock_active(mock_name, offset):
                return STD010(filepath, line, column, mock_name, f"Mock '{mock_name}' is not active at this position.")

            # Check if mock method is valid
            if method not in self.mock_methods:
                return STD002(filepath, line, column, call, f"{mock_name}.mock")

            return None

        # Check if it's a call to a mocked object (e.g. 'ls' if mocked)
        if self.file_state.is_mock_active(call, offset):
            if not is_test_file:
                 return STD007(filepath, line, column, call)
            # It's an active mock, so it's valid to call it as a command
            return None

        return None
