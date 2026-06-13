"""Validator for checking the number of arguments in standard library function calls."""

from typing import TYPE_CHECKING, List, Optional

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
        if args:
            for arg in args:
                if "${ARRAY_X}" in arg or arg in ("$@", "$*"):
                    return STD011(filepath, line, column, call)

        func_meta = self._get_meta(call, offset)
        if not func_meta:
            return None

        min_args = func_meta.get("min_args", 0)
        max_args = func_meta.get("max_args", -1)

        actual_args = len(args) if args is not None else 0

        if actual_args < min_args:
            return STD005(filepath, line, column, call, actual_args, min_args, max_args)

        if max_args != -1 and actual_args > max_args:
            return STD005(filepath, line, column, call, actual_args, min_args, max_args)

        return None

    def _get_meta(self, call: str, offset: int) -> Optional[dict]:
        if call in self.global_state.functions:
            return self.global_state.metadata.get(call)

        if self.MOCK_TOKEN in call:
            parts = call.split(self.MOCK_TOKEN, 1)
            mock_name = parts[0]
            method = parts[1]
            if self.file_state.is_mock_active(mock_name, offset):
                return self.global_state.metadata.get("{}{}".format(self.MOCK_META_PREFIX, method))

        return None
