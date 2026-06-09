"""Validator for ensuring testing functions are only used in test scripts."""

from typing import TYPE_CHECKING, List, Optional

from errors import STD007
from validators.base import ValidatorBase

if TYPE_CHECKING:
    from errors.base import LinterErrorBase


class IsTestingFunctionCallValidator(ValidatorBase):
    """Ensures testing functions are not used outside of test scripts."""

    def check(
        self,
        call: str,
        filepath: str,
        line: int,
        column: int,
        args: "Optional[List[str]]" = None,
    ) -> "Optional[LinterErrorBase]":
        func_meta = self.state.metadata.get(call)
        if not func_meta:
            return None

        if not func_meta.get("is_testing", False):
            return None

        if "test" in filepath.lower():
            return None

        return STD007(filepath, line, column, call)
