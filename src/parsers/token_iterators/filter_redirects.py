"""Iterator for filtering out shell redirections from a Bash token stream."""

import re
from typing import List


class FilterRedirectsTokenIterator:
    """Iterates over Bash tokens and skips those that are part of a redirection."""

    REDIRECT_OPERATORS = {">", ">>", "<", ">&", "<&", "<<<", "<<"}
    FD_REDIRECT_PATTERN = re.compile(r"^\d+>>?$")
    FD_REDIRECT_WITH_TARGET_PATTERN = re.compile(r"^\d+>&?$")
    SELF_CONTAINED_REDIRECT_PATTERN = re.compile(r"^\d+>&?\d+$|^\d+>/\S+$")

    def __init__(self, tokens: "List[str]") -> None:
        self.tokens = tokens
        self.index = 0

    def __iter__(self) -> "FilterRedirectsTokenIterator":
        return self

    def __next__(self) -> "str":
        while self.index < len(self.tokens):
            token = self.tokens[self.index]

            skip_count = self._get_redirect_skip_count()
            if skip_count > 0:
                self.index += skip_count
                continue

            self.index += 1
            return token

        raise StopIteration

    def _get_redirect_skip_count(self) -> "int":
        """Determine how many tokens to skip for redirections."""
        token = self.tokens[self.index]

        if self._is_prefixed_redirect():
            # Skip fd, operator, and potentially target
            return 3 if self._requires_target(self.tokens[self.index + 1]) else 2

        if self._is_redirect_operator(token):
            return 2 if self._requires_target(token) else 1

        if self._is_file_descriptor_redirect(token):
            return 2 if self._requires_target(token) else 1

        if self._is_self_contained_redirect(token):
            return 1

        return 0

    def _is_prefixed_redirect(self) -> "bool":
        return (
            self.index + 1 < len(self.tokens)
            and self.tokens[self.index].isdigit()
            and self._is_redirect_operator(self.tokens[self.index + 1])
        )

    def _is_redirect_operator(self, token: "str") -> "bool":
        return token in self.REDIRECT_OPERATORS

    def _is_file_descriptor_redirect(self, token: "str") -> "bool":
        return bool(self.FD_REDIRECT_PATTERN.match(token)) or bool(
            self.FD_REDIRECT_WITH_TARGET_PATTERN.match(token)
        )

    def _requires_target(self, token: "str") -> "bool":
        # Operators like >&1 or 2>&1 are often self-contained tokens,
        # but with punctuation_chars=True, we might see >& or >.
        # If it ends with a digit or looks like a path, it might already have a target.
        return not re.search(r"&\d+$", token) and not re.search(r"[^>]\d+$", token)

    def _is_self_contained_redirect(self, token: "str") -> "bool":
        return bool(self.SELF_CONTAINED_REDIRECT_PATTERN.match(token))
