from typing import Iterator, List, NamedTuple, Tuple, Union

from .enhanced_shlex import AdvancedToken
from .shlex import ShlexTokenIterator


class FunctionStartEvent(NamedTuple):
    name: str
    offset: int


class FunctionEndEvent(NamedTuple):
    name: str
    offset: int


class MockCreationEvent(NamedTuple):
    name: str
    offset: int


class MockDeletionEvent(NamedTuple):
    name: str
    offset: int


class MockResetEvent(NamedTuple):
    offset: int


DiscoveryEvent = Union[
    FunctionStartEvent,
    FunctionEndEvent,
    MockCreationEvent,
    MockDeletionEvent,
    MockResetEvent,
    AdvancedToken,
]


class DiscoveryTokenIterator:
    """Iterates over tokens and yields discovery events or raw tokens."""

    def __init__(self, content: str) -> None:
        self.content = content
        self.iterator = ShlexTokenIterator(content)
        self.brace_depth = 0
        self.function_stack: List[Tuple[str, int]] = []

    def __iter__(self) -> Iterator[DiscoveryEvent]:
        name: str
        try:
            for token in self.iterator:
                # 1. Check for function definitions
                if self._is_function_start(token):
                    name = token
                    if name == "function":
                        try:
                            name = next(self.iterator)
                        except StopIteration:
                            break

                    # Look for opening brace
                    for t in self.iterator:
                        if (
                            hasattr(t, "is_fully_quoted")
                            and not t.is_fully_quoted
                            and "{" in t.unquoted_specials
                        ):
                            self.brace_depth += 1
                            self.function_stack.append((name, self.brace_depth))
                            yield FunctionStartEvent(name, t.start_offset)
                            break
                        if (
                            hasattr(t, "is_fully_quoted")
                            and not t.is_fully_quoted
                            and t in [";", "\n"]
                        ):
                            continue
                        # If we find something else, it might not be a
                        # standard definition
                        yield t
                        break
                    continue

                # 2. Track brace depth and function endings
                if hasattr(token, "is_fully_quoted") and not token.is_fully_quoted:
                    if "{" in token.unquoted_specials:
                        self.brace_depth += token.count("{")
                    if "}" in token.unquoted_specials:
                        for _ in range(token.count("}")):
                            if (
                                self.function_stack
                                and self.function_stack[-1][1] == self.brace_depth
                            ):
                                name, _ = self.function_stack.pop()
                                yield FunctionEndEvent(name, token.end_offset)
                            self.brace_depth -= 1

                # 3. Check for mock events
                if hasattr(token, "is_fully_quoted") and not token.is_fully_quoted:
                    if token == "_mock.create":
                        try:
                            mock_name = next(self.iterator)
                            yield MockCreationEvent(mock_name, token.end_offset)
                        except StopIteration:
                            break
                        continue
                    elif token == "_mock.delete":
                        try:
                            mock_name = next(self.iterator)
                            yield MockDeletionEvent(mock_name, token.start_offset)
                        except StopIteration:
                            break
                        continue
                    elif token == "_mock.reset_all":
                        yield MockResetEvent(token.start_offset)
                        continue

                # 4. Default: yield the token itself
                yield token

        except (StopIteration, ValueError):
            pass

    def _is_function_start(self, token: AdvancedToken) -> bool:
        if not hasattr(token, "is_fully_quoted") or token.is_fully_quoted:
            return False

        if token == "function":
            return True

        if self.iterator.is_preceded_by_function_keyword(
            self.content[: token.start_offset]
        ):
            return True

        return False
