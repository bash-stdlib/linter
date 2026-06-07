"""Iterator for tokenizing Bash code using shlex."""

import shlex
from typing import List, Tuple

from constants import SHELL_COMMAND_SEPARATORS


class ShlexTokenIterator:
    """Iterates over tokens produced by shlex.shlex."""

    FUNCTION_KEYWORD = "function"
    WHITESPACE_CHARS = " \t\r\x0b"
    WORDCHARS_APPENDUM = "./$*?@-_"

    def __init__(self, content: "str") -> None:
        self._placeholders: "List[Tuple[str, str]]" = []
        masked_content = self._mask_content(content)

        self.lexer = shlex.shlex(masked_content, posix=True, punctuation_chars=True)
        self.lexer.whitespace = self.WHITESPACE_CHARS
        self.lexer.wordchars += self.WORDCHARS_APPENDUM
        self.parsing_error = False
        self._last_token_was_quoted = False

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
        """Check if current tokens are at the start of a command
        (only assignments or separators before).
        """
        try:
            at_start = True
            for token in self:
                if token in SHELL_COMMAND_SEPARATORS:
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

    @classmethod
    def is_in_comment(cls, line_before: str) -> bool:
        """Check if the given line content before a match contains
        an unquoted comment start.
        """
        if "#" not in line_before:
            return False

        # Use a two-lexer approach to detect unquoted '#'
        normal_lexer = shlex.shlex(line_before, posix=True, punctuation_chars=True)
        normal_lexer.whitespace = cls.WHITESPACE_CHARS
        normal_lexer.wordchars += cls.WORDCHARS_APPENDUM

        no_comment_lexer = shlex.shlex(line_before, posix=True, punctuation_chars=True)
        no_comment_lexer.whitespace = cls.WHITESPACE_CHARS
        no_comment_lexer.wordchars += cls.WORDCHARS_APPENDUM
        no_comment_lexer.commenters = ""

        try:
            while True:
                try:
                    n_token = next(normal_lexer)
                except StopIteration:
                    n_token = None

                try:
                    nc_token = next(no_comment_lexer)
                except StopIteration:
                    nc_token = None

                if n_token != nc_token:
                    # If tokens differ, it means the no_comment_lexer found something
                    # that the normal_lexer (with comments enabled) didn't,
                    # or it stopped early because of a comment.
                    # If nc_token is '#', it's a comment.
                    if nc_token == "#":
                        return True
                    # If we have a mismatch, and it's not simply the end of stream,
                    # it might be because a comment started.
                    return True

                if n_token is None and nc_token is None:
                    break
        except (ValueError, StopIteration):
            pass

        return False

    def __iter__(self) -> "ShlexTokenIterator":
        return self

    def _mask_content(self, content: str) -> str:
        import re

        pattern = r'("(?:[^"\\]|\\.)*"|\'(?:[^\'\\]|\\.)*\'|\\.)'
        self._placeholders = []

        def mask(m: "re.Match[str]") -> str:
            p = "__STDLIB_PLACEHOLDER_{}__".format(len(self._placeholders))
            self._placeholders.append((p, m.group(0)))
            return p

        return re.sub(pattern, mask, content)

    def __next__(self) -> "str":
        try:
            token = next(self.lexer)
            self._last_token_was_quoted = False

            for p, original in self._placeholders:
                if p in token:
                    self._last_token_was_quoted = True
                    # Unquote the original using shlex.split safely
                    unquoted = shlex.split(original)[0]
                    token = token.replace(p, unquoted)

            return token
        except ValueError:
            self.parsing_error = True
            raise StopIteration

    @property
    def last_token_was_quoted(self) -> bool:
        """Check if the last token returned by __next__ was quoted."""
        return self._last_token_was_quoted
