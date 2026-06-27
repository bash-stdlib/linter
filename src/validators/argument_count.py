"""Validator for checking the number of arguments in standard library function calls."""

from typing import TYPE_CHECKING, List, Optional

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

        min_args = func_meta.get("min_args", 0)
        max_args = func_meta.get("max_args", -1)

        min_guaranteed_args = 0
        has_uncertain_array = False
        if args:
            for arg in args:
                if arg.startswith(ARRAY_SIZE_PREFIX) and arg.endswith(
                    ARRAY_SIZE_SUFFIX
                ):
                    try:
                        size = int(
                            arg[len(ARRAY_SIZE_PREFIX) : -len(ARRAY_SIZE_SUFFIX)]
                        )
                        min_guaranteed_args += size
                    except ValueError:
                        min_guaranteed_args += 1
                elif (
                    ARRAY_MULTI_PLACEHOLDER in arg
                    or ARRAY_SINGLE_PLACEHOLDER in arg
                    or arg in ("$@", "$*")
                ):
                    has_uncertain_array = True
                else:
                    min_guaranteed_args += 1

        if max_args != -1 and min_guaranteed_args > max_args:
            return STD005(
                filepath, line, column, call, min_guaranteed_args, min_args, max_args
            )

        if has_uncertain_array:
            if max_args != -1:
                # If we have an upper bound, any array might push us over it.
                # However, if we are ALREADY over it, we should have caught it above.
                # If we are EXACTLY at max_args, the array will definitely push us over.
                if min_guaranteed_args >= max_args:
                    return STD005(
                        filepath,
                        line,
                        column,
                        call,
                        min_guaranteed_args + 1,
                        min_args,
                        max_args,
                    )
                return STD011(filepath, line, column, call)
            if min_guaranteed_args < min_args:
                return STD011(filepath, line, column, call)
            return None

        if min_guaranteed_args < min_args:
            return STD005(
                filepath, line, column, call, min_guaranteed_args, min_args, max_args
            )

        return None

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
