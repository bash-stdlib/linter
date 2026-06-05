"""Iterator for extracting tokens belonging to a single Bash command."""

from typing import Iterable, Iterator


class CommandsTokenIterator:
    """Iterates over tokens unil a command separator or newline is reached."""

    SHELL_SEPARATORS = {";", "|", "&", "&&", "||", ")", "}"}

    def __init__(self, token_iterator: "Iterable[str]") -> None:
        self.iterator: "Iterator[str]" = iter(token_iterator)

    def __iter__(self) -> "CommandsTokenIterator":
        return self

    def __next__(self) -> "str":
        token = next(self.iterator)

        if self._is_command_end(token):
            raise StopIteration

        return token

    def _is_command_end(self, token: "str") -> "bool":
        return token in self.SHELL_SEPARATORS or token == "\n"
