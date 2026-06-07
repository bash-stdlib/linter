"""Linter error STD005: Wrong number of arguments."""

from .base import LinterError


class STD005(LinterError):
    CODE = "STD005"
    TITLE = "wrong number of arguments"
    DESCRIPTION = "The function was called with an incorrect number of arguments."

    def __init__(
        self,
        file: str,
        line: int,
        column: int,
        match: str,
        actual_args: int,
        min_args: int,
        max_args: int,
    ) -> None:
        self.actual_args = actual_args
        self.min_args = min_args
        self.max_args = max_args
        super().__init__(file, line, column, match)

    def format_message(self) -> str:
        if self.min_args == self.max_args:
            expected = "{}".format(self.min_args)
        elif self.max_args == -1:
            expected = "at least {}".format(self.min_args)
        else:
            expected = "between {} and {}".format(self.min_args, self.max_args)

        return "'{}' expects {} arguments, but {} were provided.".format(
            self.match, expected, self.actual_args
        )
