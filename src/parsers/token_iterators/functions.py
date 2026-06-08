from typing import Iterator, Optional

from functions.scope import FunctionScope
from .shlex import ShlexTokenIterator


class FunctionDefinitionsTokenIterator:
    """Iterates over tokens to discover function definitions and their scopes."""

    def __init__(self, content: str) -> None:
        self.content = content
        self.iterator = ShlexTokenIterator(content)

    def __iter__(self) -> Iterator[FunctionScope]:
        try:
            for token in self.iterator:
                # Handle 'function name {' and 'function name() {'
                if (
                    hasattr(token, "is_fully_quoted")
                    and not token.is_fully_quoted
                    and (
                        token == "function"
                        or self.iterator.is_preceded_by_function_keyword(
                            self.content[: token.start_offset]
                        )
                    )
                ):
                    name = token
                    if name == "function":
                        try:
                            name = next(self.iterator)
                        except StopIteration:
                            break

                    # Look for opening brace or parenthesis
                    found_scope = self._find_scope(name)
                    if found_scope:
                        yield found_scope

                # Handle 'name() {'
                elif hasattr(token, "is_fully_quoted") and not token.is_fully_quoted:
                    # Check if next is ()
                    try:
                        next_token = next(self.iterator)
                        if next_token == "()" or next_token == "(":
                            if next_token == "(":
                                try:
                                    if next(self.iterator) != ")":
                                        continue
                                except StopIteration:
                                    break

                            found_scope = self._find_scope(token)
                            if found_scope:
                                yield found_scope
                        else:
                            # Not a function, backtrack or just continue
                            # (shlex doesn't easily backtrack, but we can rely on state)
                            pass
                    except StopIteration:
                        break

        except (StopIteration, ValueError):
            pass

    def _find_scope(self, name: str) -> Optional[FunctionScope]:
        """Look for opening brace and skip to balanced closing brace."""
        found_brace = False
        for t in self.iterator:
            if (
                hasattr(t, "is_fully_quoted")
                and not t.is_fully_quoted
                and "{" in t.unquoted_specials
            ):
                found_brace = True
                break
            if (
                hasattr(t, "is_fully_quoted")
                and not t.is_fully_quoted
                and t in [";", "\n"]
            ):
                continue
            # If we find something else, it might not be a standard definition
            # we support
            break

        if found_brace:
            start_offset = t.start_offset
            end_offset = self.iterator.skip_to_balanced_bracket()
            if end_offset:
                return FunctionScope(name, start_offset, end_offset)
        return None
