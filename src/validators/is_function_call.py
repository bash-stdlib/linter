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
    MOCK_META_PREFIX = "object.mock."

    def __init__(
        self, global_state: "GlobalLinterState", file_state: "FileLinterState"
    ) -> None:
        super().__init__(global_state, file_state)
        self.mock_methods: Set[str] = self._derive_mock_methods()

    def _derive_mock_methods(self) -> Set[Set[str]]:
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
            if self.file_state.is_mock_active(mock_name, offset) and method in self.mock_methods:
                return True

        return False
