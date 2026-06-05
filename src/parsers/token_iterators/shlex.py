"""Iterator for tokenizing Bash code using shlex."""

import shlex
from typing import Iterator


class ShlexTokenIterator:
    """Iterates over tokens produced by shlex.shlex."""

    WHITESPACE_CHARS = " \t\r"
    WORDCHARS_APPENDUM = "./$*?@-_"

    def __init__(self, content: "str") -> None:
        self.lexer = shlex.shlex(content, posix=True, punctuation_chars=True)
        self.lexer.whitespace = self.WHITESPACE_CHARS
        self.lexer.wordchars += self.WORDCHARS_APPENDUM
        self.parsing_error = False

    def __iter__(self) -> "ShlexTokenIterator":
        return self

    def __next__(self) -> "str":
        try:
            token = next(self.lexer)
            return token
        except ValueError:
            self.parsing_error = True
            raise StopIteration
        except StopIteration:
            raise StopIteration
