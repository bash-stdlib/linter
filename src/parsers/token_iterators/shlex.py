"""Iterator for tokenizing Bash code using shlex."""

import shlex
from typing import Optional


class ShlexTokenIterator:
    """Iterates over tokens using shlex, handling parsing errors."""

    def __init__(self, content: str, whitespace: str, wordchars: str) -> None:
        self.lexer = shlex.shlex(content, posix=True, punctuation_chars=True)
        self.lexer.whitespace = whitespace
        self.lexer.wordchars += wordchars
        self.parsing_error = False

    def __iter__(self) -> "ShlexTokenIterator":
        return self

    def __next__(self) -> str:
        try:
            token = self.lexer.get_token()
            if not token:
                raise StopIteration
            return token
        except ValueError:
            self.parsing_error = True
            raise StopIteration
