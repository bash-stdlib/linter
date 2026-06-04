"""Validator for checking the number of arguments in standard library function calls."""

from typing import TYPE_CHECKING, Any, Dict, List, Optional

from errors import STD005
from validators.base import ValidatorBase

if TYPE_CHECKING:
    from errors.base import LinterErrorBase
    from typing import Set


class ArgumentCountValidator(ValidatorBase):
    """Checks if the call has the correct number of arguments."""

    def __init__(
        self,
        functions: "Set[str]",
        namespaces: "Set[str]",
        metadata: "Dict[str, Any]",
    ) -> None:
        super().__init__(functions, namespaces)
        self.metadata = metadata

    def check(
        self,
        call: str,
        file: str,
        line: int,
        column: int,
        args: "Optional[List[str]]" = None,
    ) -> "Optional[LinterErrorBase]":
        if call not in self.functions:
            return None

        if args is None:
            args = []

        func_meta = self.metadata.get(call)
        if not func_meta:
            return None

        min_args = func_meta.get("min_args", 0)
        max_args = func_meta.get("max_args", 0)
        actual_args = len(args)

        is_valid = True
        if actual_args < min_args:
            is_valid = False
        elif max_args != -1 and actual_args > max_args:
            is_valid = False

        if not is_valid:
            return STD005(file, line, column, call, actual_args, min_args, max_args)

        return None
