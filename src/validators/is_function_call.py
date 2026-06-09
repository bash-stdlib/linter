"""ValidatorBase for valid standard library function calls."""

from typing import TYPE_CHECKING, List, Optional

from errors import STD001, STD002, STD004
from validators.base import ValidatorBase

if TYPE_CHECKING:
    from errors.base import LinterErrorBase


class IsFunctionCallValidator(ValidatorBase):
    """Checks if the call is a valid function or a misnamed one."""

    WHITELISTED_PREFIXES = ["assert_"]

    def check(
        self,
        call: str,
        filepath: str,
        line: int,
        column: int,
        args: "Optional[List[str]]" = None,
    ) -> "Optional[LinterErrorBase]":
        if call in self.global_state.functions:
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
