"""ValidatorBase for valid standard library function calls."""

from typing import List, Optional

from errors import STD001, STD002, STD004
from errors.base import LinterErrorBase
from validators.base import ValidatorBase


class IsFunctionCallValidator(ValidatorBase):
    """Checks if the call is a valid function or a misnamed one."""

    def check(
        self,
        call: str,
        file: str,
        line: int,
        column: int,
        args: "Optional[List[str]]" = None,
    ) -> Optional[LinterErrorBase]:
        if call in self.functions:
            return None

        longest_namespace = self._find_longest_namespace_prefix(call)

        if longest_namespace:
            if self._is_immediate_child_of_namespace(call, longest_namespace):
                suggestion = self._get_suggestion(call, longest_namespace)
                return STD002(file, line, column, call, longest_namespace, suggestion)

            invalid_namespace = self._extract_invalid_namespace(call, longest_namespace)
            return STD001(file, line, column, call, invalid_namespace)

        return STD004(file, line, column, call)
