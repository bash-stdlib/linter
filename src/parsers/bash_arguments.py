"""Bash argument parser for extracting arguments from function calls."""

import re
import shlex
from typing import List, Optional

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

            if self._is_start_of_subshell(token, tokens, index):
                full_subshell, next_index = self._consume_subshell(tokens, index)
                args.append(full_subshell)
                index = next_index
                continue

            if self._is_start_of_parameter_expansion(token, tokens, index):
                full_expansion, next_index = self._consume_parameter_expansion(tokens, index)
                args.append(full_expansion)
                index = next_index
                continue

            if self._is_start_of_backticks(token):
                full_backtick, next_index = self._consume_backticks(tokens, index)
                args.append(full_backtick)
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

    def _is_start_of_subshell(
        self, token: "str", tokens: "List[str]", index: "int"
    ) -> "bool":
        return token == "$" and index + 1 < len(tokens) and tokens[index + 1] == "("

    def _is_start_of_parameter_expansion(
        self, token: "str", tokens: "List[str]", index: "int"
    ) -> "bool":
        return token == "$" and index + 1 < len(tokens) and tokens[index + 1] == "{"

    def _is_start_of_backticks(self, token: "str") -> "bool":
        return token == "`"

    def _consume_subshell(self, tokens: "List[str]", start_index: "int") -> "tuple":
        """Consumes tokens belonging to a $(...) subshell, handling nesting."""
        level = 1
        consumed = ["$", "("]
        index = start_index + 2

        while index < len(tokens):
            token = tokens[index]
            if token == "(":
                level += 1
            elif token == ")":
                level -= 1
                if level == 0:
                    consumed.append(token)
                    index += 1
                    break

            if token == "))":
                level -= 2
                if level <= 0:
                    consumed.append("))")
                    index += 1
                    break

            # To accurately reconstruct the argument, we'd need whitespace info.
            # Since we don't have it, we just append tokens.
            # In many cases this is fine for COUNTING arguments.
            consumed.append(token)
            index += 1

        return "".join(consumed), index

    def _consume_parameter_expansion(self, tokens: "List[str]", start_index: "int") -> "tuple":
        """Consumes tokens belonging to a ${...} parameter expansion."""
        level = 1
        consumed = ["$", "{"]
        index = start_index + 2

        while index < len(tokens):
            token = tokens[index]
            if token == "{":
                level += 1
            elif token == "}":
                level -= 1
                if level == 0:
                    consumed.append(token)
                    index += 1
                    break

            consumed.append(token)
            index += 1

        return "".join(consumed), index

    def _consume_backticks(self, tokens: "List[str]", start_index: "int") -> "tuple":
        """Consumes tokens belonging to a `...` backtick command, handling nesting."""
        consumed = ["`"]
        index = start_index + 1

        while index < len(tokens):
            token = tokens[index]

            # Handle escaped backticks for nesting
            if token == "\\" and index + 1 < len(tokens) and tokens[index + 1] == "`":
                consumed.append("\\`")
                index += 2
                continue

            consumed.append(token)
            if token == "`":
                index += 1
                break
            index += 1

        return "".join(consumed), index

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
        return not re.search(r"&\d+$", token) and not re.search(r"[^>]\d+$", token)

    def _is_self_contained_redirect(self, token: "str") -> "bool":
        return bool(self.SELF_CONTAINED_REDIRECT_PATTERN.match(token))
