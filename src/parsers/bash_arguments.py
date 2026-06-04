"""Bash argument parser for extracting arguments from function calls."""

import re
import shlex
from typing import List, Optional

from .base import ParserBase


class BashArgumentsParser(ParserBase):
    """Parses Bash code to extract arguments following a function call."""

    SHELL_SEPARATORS = {";", "|", "&", "&&", "||", ")"}
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
        i = 0

        while i < len(tokens):
            token = tokens[i]

            if self._is_command_end(token):
                break

            if self._is_start_of_subshell(token, tokens, i):
                full_subshell, next_i = self._consume_subshell(tokens, i)
                args.append(full_subshell)
                i = next_i
                continue

            if self._is_start_of_backticks(token):
                full_backtick, next_i = self._consume_backticks(tokens, i)
                args.append(full_backtick)
                i = next_i
                continue

            skip_count = self._get_redirect_skip_count(tokens, i)
            if skip_count > 0:
                i += skip_count
                continue

            args.append(token)
            i += 1

        return args

    def _is_command_end(self, token: "str") -> "bool":
        return token in self.SHELL_SEPARATORS or token == "\n"

    def _is_start_of_subshell(self, token: "str", tokens: "List[str]", i: "int") -> "bool":
        return token == "$" and i + 1 < len(tokens) and tokens[i + 1] == "("

    def _is_start_of_backticks(self, token: "str") -> "bool":
        return token == "`"

    def _consume_subshell(self, tokens: "List[str]", start_index: "int") -> "tuple":
        """Consumes tokens belonging to a $(...) subshell."""
        # tokens[start_index] is '$', tokens[start_index+1] is '('
        level = 1
        consumed = ["$", "("]
        i = start_index + 2

        while i < len(tokens):
            t = tokens[i]
            if t == "(":
                level += 1
            elif t == ")":
                level -= 1
                if level == 0:
                    consumed.append(t)
                    i += 1
                    break

            # Handle '))' as split into ')' and ')'
            if t == "))":
                 level -= 2
                 if level <= 0:
                     consumed.append("))")
                     i += 1
                     break

            if self._should_insert_space(consumed, t):
                 consumed.append(" ")

            consumed.append(t)
            i += 1

        return "".join(consumed), i

    def _should_insert_space(self, consumed: "List[str]", next_token: "str") -> "bool":
        if not consumed:
            return False
        if consumed[-1] in ["(", "$"]:
            return False
        if next_token in [")", "(", " "]:
            return False
        return True

    def _consume_backticks(self, tokens: "List[str]", start_index: "int") -> "tuple":
        """Consumes tokens belonging to a `...` backtick command."""
        consumed = ["`"]
        i = start_index + 1

        while i < len(tokens):
            t = tokens[i]
            if consumed and consumed[-1] != "`" and t != "`":
                consumed.append(" ")
            consumed.append(t)
            if t == "`":
                i += 1
                break
            i += 1

        return "".join(consumed), i

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

    def _is_prefixed_redirect(self, tokens: "List[str]", i: "int") -> "bool":
        return (
            i + 1 < len(tokens)
            and tokens[i].isdigit()
            and self._is_redirect_operator(tokens[i + 1])
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
