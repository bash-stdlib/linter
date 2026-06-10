"""Iterator for tokenizing Bash code using shlex."""

from typing import TYPE_CHECKING

from constants import SHELL_COMMAND_SEPARATORS
from .enhanced_shlex import EnhancedShlex

if TYPE_CHECKING:
    from .enhanced_shlex import AdvancedToken


class ShlexTokenIterator:
    """Iterates over tokens produced by shlex.shlex."""

    FUNCTION_KEYWORD = "function"
    WHITESPACE_CHARS = " \t\r\x0b"
    WORDCHARS_APPENDUM = "./$*?@-_"
    COMMENT_CHAR = "#"

    def __init__(self, content: "str") -> None:
        target_chars = list(SHELL_COMMAND_SEPARATORS) + [">", "<"]
        self.lexer = EnhancedShlex(
            content, posix=True, target_chars=target_chars, punctuation_chars=True
        )
        self.lexer.whitespace = self.WHITESPACE_CHARS
        # Ensure WORDCHARS_APPENDUM does not include any target_chars
        wordchars = "".join(c for c in self.WORDCHARS_APPENDUM if c not in target_chars)
        self.lexer.wordchars += wordchars
        self.parsing_error = False

    @classmethod
    def is_preceded_by_function_keyword(cls, content_before: str) -> bool:
        """Check if the content before a match ends with the 'function' keyword."""
        before = content_before.rstrip()
        if before.endswith(cls.FUNCTION_KEYWORD):
            # Ensure it's a whole word
            keyword_len = len(cls.FUNCTION_KEYWORD)
            if len(before) == keyword_len or not before[-(keyword_len + 1)].isalnum():
                return True
        return False

    def is_function_definition(self) -> bool:
        """Check if the next tokens indicate a function definition."""
        try:
            first_token = next(self)
            if first_token == "()":
                return True
            if first_token == "(":
                second_token = next(self)
                if second_token == ")":
                    return True
        except StopIteration:
            pass
        return False

    def is_at_command_position(self) -> bool:
        """Check if current tokens are at the start of a command.

        This means only assignments or separators occur before it.
        """
        try:
            at_start = True
            for token in self:
                if (
                    hasattr(token, "unquoted_specials")
                    and self.COMMENT_CHAR in token.unquoted_specials
                    and token.startswith(self.COMMENT_CHAR)
                ):
                    return False

                if hasattr(token, "is_fully_quoted"):
                    is_quoted = getattr(token, "is_fully_quoted")
                else:
                    is_quoted = False

                if not is_quoted and token in SHELL_COMMAND_SEPARATORS:
                    at_start = True
                    continue

                if token == "$":
                    continue
                if "=" in token and at_start:
                    continue

                at_start = False
            return at_start
        except (StopIteration, ValueError):
            return True

    def __iter__(self) -> "ShlexTokenIterator":
        return self

    def __next__(self) -> "AdvancedToken":
        try:
            token = next(self.lexer)
            return token
        except ValueError:
            self.parsing_error = True
            raise StopIteration
