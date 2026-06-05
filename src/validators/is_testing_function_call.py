"""Validator for ensuring testing functions are only used in test scripts."""

from typing import TYPE_CHECKING, Any, Dict, List, Optional

from errors import STD007
from validators.base import ValidatorBase

if TYPE_CHECKING:
    from typing import Set
    from errors.base import LinterErrorBase


class IsTestingFunctionCallValidator(ValidatorBase):
    """Ensures testing functions are not used outside of test scripts."""

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
        filepath: str,
        line: int,
        column: int,
        args: "Optional[List[str]]" = None,
    ) -> "Optional[LinterErrorBase]":
        func_meta = self.metadata.get(call)
        if not func_meta:
            return None

        if not func_meta.get("is_testing", False):
            return None

        if "test" in filepath.lower():
            return None

        return STD007(filepath, line, column, call)
