"""Iterator for filtering out shell redirections from a Bash token stream."""

import re
from collections import deque
from typing import Iterable, Iterator, Optional


class FilterRedirectsTokenIterator:
    """Iterates over Bash tokens and skips those that are part of a redirection."""

    REDIRECT_OPERATORS = {">", ">>", "<", ">&", "<&", "<<<", "<<", ">&"}
    FD_REDIRECT_PATTERN = re.compile(r"^\d+>>?$")
    FD_REDIRECT_WITH_TARGET_PATTERN = re.compile(r"^\d+>&?$")
    SELF_CONTAINED_REDIRECT_PATTERN = re.compile(r"^\d+>&?\d+$|^\d+>/\S+$")

    def __init__(self, tokens: "Iterable[str]") -> None:
        self.iterator: "Iterator[str]" = iter(tokens)
        self.lookahead: "deque[str]" = deque()

    def __iter__(self) -> "FilterRedirectsTokenIterator":
        return self

    def _peek(self, n: "int" = 0) -> "Optional[str]":
        """Peek at the n-th token ahead (0-indexed)."""
        while len(self.lookahead) <= n:
            try:
                self.lookahead.append(next(self.iterator))
            except StopIteration:
                return None
        return self.lookahead[n]

    def _consume(self) -> "str":
        """Consume and return the next token."""
        if self.lookahead:
            return self.lookahead.popleft()
        return next(self.iterator)

    def __next__(self) -> "str":
        while True:
            token = self._peek(0)
            if token is None:
                raise StopIteration

            skip_count = self._get_redirect_skip_count()
            if skip_count > 0:
                for _ in range(skip_count):
                    self._consume()
                continue

            return self._consume()

    def _get_redirect_skip_count(self) -> "int":
        """Determine how many tokens to skip for redirections."""
        token = self._peek(0)
        if token is None:
            return 0

        if self._is_prefixed_redirect():
            # Skip fd, operator, and potentially target
            op = self._peek(1)
            return 3 if op is not None and self._requires_target(op) else 2

        if self._is_redirect_operator(token):
            return 2 if self._requires_target(token) else 1

        if self._is_file_descriptor_redirect(token):
            return 2 if self._requires_target(token) else 1

        if self._is_self_contained_redirect(token):
            return 1

        return 0

    def _is_prefixed_redirect(self) -> "bool":
        token = self._peek(0)
        next_token = self._peek(1)
        if token is None or next_token is None:
            return False

        is_quoted_token = getattr(token, "is_fully_quoted", False)
        is_quoted_next = getattr(next_token, "is_fully_quoted", False)

        return (
            not is_quoted_token
            and token.isdigit()
            and not is_quoted_next
            and self._is_redirect_operator(next_token)
        )

    def _is_redirect_operator(self, token: "str") -> "bool":
        is_quoted = getattr(token, "is_fully_quoted", False)
        return not is_quoted and token in self.REDIRECT_OPERATORS

    def _is_file_descriptor_redirect(self, token: "str") -> "bool":
        is_quoted = getattr(token, "is_fully_quoted", False)
        return not is_quoted and (
            bool(self.FD_REDIRECT_PATTERN.match(token))
            or bool(self.FD_REDIRECT_WITH_TARGET_PATTERN.match(token))
        )

    def _requires_target(self, token: "str") -> "bool":
        # Operators like >&1 or 2>&1 are often self-contained tokens,
        # but with punctuation_chars=True, we might see >& or >.
        # If it ends with a digit or looks like a path, it might already have a target.
        return not re.search(r"&\d+$", token) and not re.search(r"[^>]\d+$", token)

    def _is_self_contained_redirect(self, token: "str") -> "bool":
        is_quoted = getattr(token, "is_fully_quoted", False)
        return not is_quoted and bool(self.SELF_CONTAINED_REDIRECT_PATTERN.match(token))
