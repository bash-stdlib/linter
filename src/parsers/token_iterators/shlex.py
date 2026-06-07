"""Iterator for tokenizing Bash code using shlex."""

import shlex


from constants import SHELL_COMMAND_SEPARATORS


class ShlexTokenIterator:
    """Iterates over tokens produced by shlex.shlex."""

    FUNCTION_KEYWORD = "function"
    WHITESPACE_CHARS = " \t\r\x0b"
    WORDCHARS_APPENDUM = "./$*?@-_"

    def __init__(self, content: "str") -> None:
        self.content = content
        self.lexer = shlex.shlex(content, posix=True, punctuation_chars=True)
        self.lexer.whitespace = self.WHITESPACE_CHARS
        self.lexer.wordchars += self.WORDCHARS_APPENDUM
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
        """Check if current tokens are at the start of a command (only assignments or separators before)."""
        # We need to detect if there is an unquoted # before the end of the content.
        # Since is_at_command_position is called on the substring before the match,
        # if a # is found, the match must be inside a comment.
        lexer = shlex.shlex(self.content, posix=True, punctuation_chars=True)
        lexer.commenters = ""
        lexer.whitespace = self.WHITESPACE_CHARS
        lexer.wordchars += self.WORDCHARS_APPENDUM

        # Track if we are at the beginning of a command
        at_start = True
        try:
            for token in lexer:
                if token == "#":
                    return False
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

    def __iter__(self) -> "ShlexTokenIterator":
        return self

    def __next__(self) -> "str":
        try:
            token = next(self.lexer)
            return token
        except ValueError:
            self.parsing_error = True
            raise StopIteration
