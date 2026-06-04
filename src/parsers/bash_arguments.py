"""Bash argument parser for extracting arguments from function calls."""

import re
import shlex
from typing import Dict, List, Optional, Tuple

from .base import ParserBase


class BashArgumentsParser(ParserBase):
    """Parses Bash code to extract arguments following a function call."""

    SHELL_SEPARATORS = {";", "|", "&", "&&", "||", ")", "}"}
    REDIRECT_OPERATORS = {">", ">>", "<", ">&", "<&", "<<<", "<<"}
    FD_REDIRECT_PATTERN = re.compile(r"^\d+>>?$")
    FD_REDIRECT_WITH_TARGET_PATTERN = re.compile(r"^\d+>&?$")
    SELF_CONTAINED_REDIRECT_PATTERN = re.compile(r"^\d+>&?\d+$|^\d+>/\S+$")
    WHITESPACE_CHARS = " \t\r"
    WORDCHARS_APPENDUM = "./$*?@-_"

    # Configuration for nested entities: (start_tokens, end_tokens, can_nest, escape_char)
    NESTED_CONFIG = {
        "$(": {"end": ")", "can_nest": True, "escape": None},
        "${": {"end": "}", "can_nest": True, "escape": None},
        "`": {"end": "`", "can_nest": True, "escape": "\\"},
    }

    def parse(self, content: "str") -> "Optional[List[str]]":
        """Extract arguments from the given Bash code string."""
        content = self._remove_line_continuations(content)

        try:
            lexer = shlex.shlex(content, posix=True, punctuation_chars=True)
            lexer.whitespace = self.WHITESPACE_CHARS
            lexer.wordchars += self.WORDCHARS_APPENDUM

            return self._extract_arguments_from_lexer(lexer)
        except Exception:
            return None

    def _remove_line_continuations(self, content: "str") -> "str":
        return content.replace("\\\n", "")

    def _extract_arguments_from_lexer(self, lexer: "shlex.shlex") -> "List[str]":
        args = []
        tokens = list(lexer)
        index = 0

        while index < len(tokens):
            token = tokens[index]

            if self._is_command_end(token):
                break

            # Handle nested entities like $(...), ${...}, `...`
            nested_start = self._get_nested_start(tokens, index)
            if nested_start:
                full_entity, next_index = self._consume_nested_entity(
                    tokens, index, nested_start
                )
                args.append(full_entity)
                index = next_index
                continue

            skip_count = self._get_redirect_skip_count(tokens, index)
            if skip_count > 0:
                index += skip_count
                continue

            args.append(token)
            index += 1

        return args

    def _is_command_end(self, token: "str") -> "bool":
        return token in self.SHELL_SEPARATORS or token == "\n"

    def _get_nested_start(self, tokens: "List[str]", index: "int") -> "Optional[str]":
        token = tokens[index]
        if token == "$":
            if index + 1 < len(tokens):
                potential_start = "$" + tokens[index + 1]
                if potential_start in self.NESTED_CONFIG:
                    return potential_start
        if token in self.NESTED_CONFIG:
            return token
        return None

    def _consume_nested_entity(
        self, tokens: "List[str]", start_index: "int", start_marker: "str"
    ) -> "Tuple[str, int]":
        """Generalized method to consume nested Bash entities."""
        config = self.NESTED_CONFIG[start_marker]
        end_marker = config["end"]
        can_nest = config["can_nest"]
        escape_char = config["escape"]

        consumed = [start_marker]
        index = start_index + len(start_marker)

        # shlex split $( and ${ into two tokens
        if start_marker in ["$(", "${"]:
            index = start_index + 2

        level = 1

        while index < len(tokens):
            token = tokens[index]

            # Handle escapes
            if escape_char and token == escape_char and index + 1 < len(tokens):
                next_token = tokens[index + 1]
                if next_token == end_marker:
                    consumed.append(escape_char + next_token)
                    index += 2
                    continue

            if can_nest and self._is_same_nested_start(token, tokens, index, start_marker):
                level += 1
                # If start_marker is multi-char, we need to consume the extra token
                if len(start_marker) > 1:
                    consumed.append(start_marker)
                    index += 2
                    continue
            elif token == end_marker:
                level -= 1
                if level == 0:
                    consumed.append(token)
                    index += 1
                    break

            # Special case for )) split by shlex
            if token == "))" and end_marker == ")":
                level -= 2
                if level <= 0:
                    consumed.append("))")
                    index += 1
                    break

            if self._should_insert_space(consumed, token):
                consumed.append(" ")

            consumed.append(token)
            index += 1

        return "".join(consumed), index

    def _is_same_nested_start(
        self, token: "str", tokens: "List[str]", index: "int", start_marker: "str"
    ) -> "bool":
        if len(start_marker) == 1:
            # Avoid matching end_marker as a new start if they are the same (like `)
            config = self.NESTED_CONFIG[start_marker]
            if token == start_marker and token != config["end"]:
                 return True
            return False

        return (
            token == start_marker[0]
            and index + 1 < len(tokens)
            and tokens[index + 1] == start_marker[1]
        )

    def _should_insert_space(self, consumed: "List[str]", next_token: "str") -> "bool":
        if not consumed:
            return False
        last = consumed[-1]
        if last in ["(", "$", "{"] or last.endswith(("${", "$(")):
            return False
        if next_token in [")", "(", "}", "{", " "]:
            return False
        return True

    def _get_redirect_skip_count(self, tokens: "List[str]", current_index: "int") -> "int":
        """Determines how many tokens to skip if a redirection is encountered."""
        token = tokens[current_index]

        if self._is_prefixed_redirect(tokens, current_index):
            return 3 if self._requires_target(tokens[current_index + 1]) else 2

        if self._is_redirect_operator(token):
            return 2 if self._requires_target(token) else 1

        if self._is_file_descriptor_redirect(token):
            return 2 if self._requires_target(token) else 1

        if self._is_self_contained_redirect(token):
            return 1

        return 0

    def _is_prefixed_redirect(self, tokens: "List[str]", index: "int") -> "bool":
        return (
            index + 1 < len(tokens)
            and tokens[index].isdigit()
            and self._is_redirect_operator(tokens[index + 1])
        )

    def _is_redirect_operator(self, token: "str") -> "bool":
        return token in self.REDIRECT_OPERATORS

    def _is_file_descriptor_redirect(self, token: "str") -> "bool":
        return bool(self.FD_REDIRECT_PATTERN.match(token)) or bool(
            self.FD_REDIRECT_WITH_TARGET_PATTERN.match(token)
        )

    def _requires_target(self, token: "str") -> "bool":
        # Operators like >&1 or 2>&1 are often self-contained tokens in some lexer modes,
        # but with punctuation_chars=True, we might see >& or >.
        # If it ends with a digit, it might already have a target.
        return not re.search(r"&\d+$", token) and not re.search(r"[^>]\d+$", token)

    def _is_self_contained_redirect(self, token: "str") -> "bool":
        return bool(self.SELF_CONTAINED_REDIRECT_PATTERN.match(token))
