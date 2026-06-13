"""ValidatorBase for valid standard library function calls."""

from typing import TYPE_CHECKING, List, Optional, Set

from issues import STD001, STD002, STD004
from validators.base import ValidatorBase

if TYPE_CHECKING:
    from issues.base import LinterIssueBase
    from linter.state.file_state import FileLinterState
    from linter.state.global_state import GlobalLinterState


class IsFunctionCallValidator(ValidatorBase):
    """Checks if the call is a valid function or a misnamed one."""

    WHITELISTED_PREFIXES = ["assert_"]
    MOCK_TOKEN = ".mock."

    def check(
        self,
        call: str,
        filepath: str,
        line: int,
        column: int,
        args: "Optional[List[str]]" = None,
        offset: int = 0,
    ) -> "Optional[LinterIssueBase]":
        if self._is_valid_call(call, offset):
            return None

        for prefix in self.WHITELISTED_PREFIXES:
            if call.startswith(prefix):
                return None

        longest_namespace = self._find_longest_namespace_prefix(call)

        if longest_namespace:
            if self._is_immediate_child_of_namespace(call, longest_namespace):
                suggestion = self._get_suggestion(call, longest_namespace)
                return STD002(
                    filepath, line, column, call, longest_namespace, suggestion
                )

            invalid_namespace = self._extract_invalid_namespace(call, longest_namespace)
            return STD001(filepath, line, column, call, invalid_namespace)

        return STD004(filepath, line, column, call)

    def _is_valid_call(self, call: str, offset: int) -> bool:
        """Verify if the call is a known function, an active mock, or a valid mock method."""
        if call in self.global_state.functions:
            return True

        if self.file_state.is_mock_active(call, offset):
            return True

        if self.MOCK_TOKEN in call:
            parts = call.split(self.MOCK_TOKEN, 1)
            mock_name = parts[0]
            method = parts[1]
            if self.file_state.is_mock_active(mock_name, offset) and method in self.global_state.mock_methods:
                return True

        return False
