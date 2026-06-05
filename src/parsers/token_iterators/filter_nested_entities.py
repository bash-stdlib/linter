"""Iterator for grouping nested Bash tokens into single logical entities."""

from collections import deque
from typing import Iterable, Iterator, Optional


class FilterNestedEntitiesTokenIterator:
    """Iterates over Bash tokens, grouping nested entities into single tokens."""

    NESTED_CONFIG = {
        "$(": {"end": ")", "can_nest": True, "escape": None},
        "${": {"end": "}", "can_nest": True, "escape": None},
        "`": {"end": "`", "can_nest": True, "escape": "\\"},
    }

    def __init__(self, tokens: "Iterable[str]") -> None:
        self.iterator: "Iterator[str]" = iter(tokens)
        self.lookahead: "deque[str]" = deque()

    def __iter__(self) -> "FilterNestedEntitiesTokenIterator":
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
        token = self._peek(0)
        if token is None:
            raise StopIteration

        nested_start = self._get_nested_start(token)

        if nested_start:
            return self._consume_nested_entity(nested_start)

        return self._consume()

    def _get_nested_start(self, token: "str") -> "Optional[str]":
        if token == "$":
            next_token = self._peek(1)
            if next_token:
                potential_start = "$" + next_token
                if potential_start in self.NESTED_CONFIG:
                    return potential_start
        if token in self.NESTED_CONFIG:
            return token
        return None

    def _consume_nested_entity(self, start_marker: "str") -> "str":
        config = self.NESTED_CONFIG[start_marker]
        end_marker = str(config["end"])
        can_nest = bool(config["can_nest"])
        escape_char = config["escape"]
        if escape_char is not None:
            escape_char = str(escape_char)

        consumed = [start_marker]

        # shlex split $( and ${ into two tokens
        if start_marker in ["$(", "${"]:
            self._consume()  # consume '$'
            self._consume()  # consume '(' or '{'
        else:
            self._consume()  # consume '`'

        level = 1

        while True:
            token = self._peek(0)
            if token is None:
                break

            if escape_char and token == escape_char and self._peek(1) == end_marker:
                self._consume()  # consume escape_char
                next_token = self._consume()  # consume end_marker
                consumed.append(escape_char + next_token)
                continue

            if can_nest and self._is_same_nested_start(token, start_marker):
                level += 1
                if len(start_marker) > 1:
                    self._consume()  # consume '$'
                    self._consume()  # consume '(' or '{'
                    consumed.append(start_marker)
                    continue
                else:
                    consumed.append(self._consume())
                    continue
            elif token == end_marker:
                level -= 1
                if level == 0:
                    consumed.append(self._consume())
                    break

            if token == "))" and end_marker == ")":
                level -= 2
                if level <= 0:
                    consumed.append(self._consume())
                    break

            consumed.append(self._consume())

        return "".join(consumed)

    def _is_same_nested_start(self, token: "str", start_marker: "str") -> "bool":
        if len(start_marker) == 1:
            config = self.NESTED_CONFIG[start_marker]
            return token == start_marker and token != config["end"]

        return token == start_marker[0] and self._peek(1) == start_marker[1]
