"""Validator for checking the number of arguments in standard library function calls."""

from typing import TYPE_CHECKING, List, Optional, Tuple

from constants import (
    ARRAY_MULTI_PLACEHOLDER,
    ARRAY_SINGLE_PLACEHOLDER,
    ARRAY_SIZE_PREFIX,
    ARRAY_SIZE_SUFFIX,
)
from issues import STD005, STD011
from validators.base import ValidatorBase

if TYPE_CHECKING:
    from issues.base import LinterIssueBase


class ArgumentCountValidator(ValidatorBase):
    """Checks if the call has the correct number of arguments."""

    MOCK_TOKEN = ".mock."
    MOCK_META_PREFIX = "object.mock."

    def check(
        self,
        call: str,
        filepath: str,
        line: int,
        column: int,
        args: "Optional[List[str]]" = None,
        offset: int = 0,
    ) -> "Optional[LinterIssueBase]":
        func_meta = self._get_meta(call, offset)
        if not func_meta:
            return None

        min_required = func_meta.get("min_args", 0)
        max_allowed = func_meta.get("max_args", -1)

        guaranteed_count, has_dynamic_args = self._analyze_arguments(args or [])

        if max_allowed != -1 and guaranteed_count > max_allowed:
            return STD005(
                filepath, line, column, call, guaranteed_count, min_required, max_allowed
            )

        if has_dynamic_args:
            if max_allowed != -1:
                if guaranteed_count >= max_allowed:
                    return STD005(
                        filepath,
                        line,
                        column,
                        call,
                        guaranteed_count + 1,
                        min_required,
                        max_allowed,
                    )
                return STD011(filepath, line, column, call)

            if guaranteed_count < min_required:
                return STD011(filepath, line, column, call)

            return None

        if guaranteed_count < min_required:
            return STD005(
                filepath, line, column, call, guaranteed_count, min_required, max_allowed
            )

        return None

    def _analyze_arguments(self, args: List[str]) -> "Tuple[int, bool]":
        guaranteed_count = 0
        has_dynamic_args = False

        for arg in args:
            if arg.startswith(ARRAY_SIZE_PREFIX) and arg.endswith(ARRAY_SIZE_SUFFIX):
                try:
                    size_str = arg[len(ARRAY_SIZE_PREFIX) : -len(ARRAY_SIZE_SUFFIX)]
                    guaranteed_count += int(size_str)
                except ValueError:
                    guaranteed_count += 1
            elif (
                ARRAY_MULTI_PLACEHOLDER in arg
                or ARRAY_SINGLE_PLACEHOLDER in arg
                or arg in ("$@", "$*")
            ):
                has_dynamic_args = True
            else:
                guaranteed_count += 1

        return guaranteed_count, has_dynamic_args

    def _get_meta(self, call: str, offset: int) -> Optional[dict]:
        if call in self.global_state.functions:
            return self.global_state.metadata.get(call)

        if self.MOCK_TOKEN in call:
            parts = call.split(self.MOCK_TOKEN, 1)
            mock_name = parts[0]
            method = parts[1]
            if self.file_state.is_mock_active(mock_name, offset):
                return self.global_state.metadata.get(
                    "{}{}".format(self.MOCK_META_PREFIX, method)
                )

        return None
