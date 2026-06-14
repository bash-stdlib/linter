"""Linter warning STD011: Array used as arguments."""

from .base import LinterWarningBase


class STD011(LinterWarningBase):
    CODE = "STD011"
    TITLE = "array used as arguments"
    DESCRIPTION = (
        "An array is being used to pass arguments. The linter cannot guarantee the "
        "contract of the function is being honoured."
    )

    def format_message(self) -> str:
        return "Array used as arguments for '{}'. Function contract cannot be guaranteed.".format(self.match)
