"""Iterator for grouping nested Bash tokens into single logical entities."""

from typing import Dict, List, Optional, Tuple


class TokenIteratorFilterNestedEntities:
    """Iterates over Bash tokens, grouping nested entities into single tokens."""

    NESTED_CONFIG = {
        "$(": {"end": ")", "can_nest": True, "escape": None},
        "${": {"end": "}", "can_nest": True, "escape": None},
        "`": {"end": "`", "can_nest": True, "escape": "\\"},
    }

    def __init__(self, tokens: "List[str]") -> None:
        self.tokens = tokens
        self.index = 0

    def __iter__(self) -> "TokenIteratorFilterNestedEntities":
        return self

    def __next__(self) -> "str":
        if self.index >= len(self.tokens):
            raise StopIteration

        token = self.tokens[self.index]
        nested_start = self._get_nested_start(token)

        if nested_start:
            return self._consume_nested_entity(nested_start)

        self.index += 1
        return token

    def _get_nested_start(self, token: "str") -> "Optional[str]":
        if token == "$":
            if self.index + 1 < len(self.tokens):
                potential_start = "$" + self.tokens[self.index + 1]
                if potential_start in self.NESTED_CONFIG:
                    return potential_start
        if token in self.NESTED_CONFIG:
            return token
        return None

    def _consume_nested_entity(self, start_marker: "str") -> "str":
        config = self.NESTED_CONFIG[start_marker]
        end_marker = config["end"]
        can_nest = config["can_nest"]
        escape_char = config["escape"]

        consumed = [start_marker]
        self.index += len(start_marker)

        # shlex split $( and ${ into two tokens
        if start_marker in ["$(", "${"]:
            self.index = self.index - len(start_marker) + 2

        level = 1

        while self.index < len(self.tokens):
            token = self.tokens[self.index]

            if escape_char and token == escape_char and self.index + 1 < len(self.tokens):
                next_token = self.tokens[self.index + 1]
                if next_token == end_marker:
                    consumed.append(escape_char + next_token)
                    self.index += 2
                    continue

            if can_nest and self._is_same_nested_start(token, start_marker):
                level += 1
                if len(start_marker) > 1:
                    consumed.append(start_marker)
                    self.index += 2
                    continue
                else:
                    consumed.append(token)
                    self.index += 1
                    continue
            elif token == end_marker:
                level -= 1
                if level == 0:
                    consumed.append(token)
                    self.index += 1
                    break

            if token == "))" and end_marker == ")":
                level -= 2
                if level <= 0:
                    consumed.append("))")
                    self.index += 1
                    break

            consumed.append(token)
            self.index += 1

        return "".join(consumed)

    def _is_same_nested_start(self, token: "str", start_marker: "str") -> "bool":
        if len(start_marker) == 1:
            config = self.NESTED_CONFIG[start_marker]
            return token == start_marker and token != config["end"]

        return (
            token == start_marker[0]
            and self.index + 1 < len(self.tokens)
            and self.tokens[self.index + 1] == start_marker[1]
        )
