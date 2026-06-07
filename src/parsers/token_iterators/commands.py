"""Iterator for extracting tokens belonging to a single Bash command."""

from typing import Iterable, Iterator

from constants import SHELL_COMMAND_SEPARATORS


class CommandsTokenIterator:
    """Iterates over tokens unil a command separator or newline is reached."""

    def __init__(self, token_iterator: "Iterable[str]") -> None:
        self.iterator: "Iterator[str]" = iter(token_iterator)
        self.stopped_at_separator = False

    def __iter__(self) -> "CommandsTokenIterator":
        return self

    def __next__(self) -> "str":
        if self.stopped_at_separator:
            raise StopIteration

        token = next(self.iterator)

        if self._is_command_end(token):
            self.stopped_at_separator = True
            raise StopIteration

        return token

    def _is_command_end(self, token: "str") -> "bool":
        if hasattr(token, "is_fully_quoted"):
            if getattr(token, "is_fully_quoted"):
                return False
            return token in SHELL_COMMAND_SEPARATORS

        return token in SHELL_COMMAND_SEPARATORS
