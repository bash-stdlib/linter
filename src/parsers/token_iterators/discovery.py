from typing import Iterator, List, Tuple, Union

from .discovery_events.base import DiscoveryEvent
from .discovery_events.functions import FunctionEndEvent, FunctionStartEvent
from .discovery_events.mocks import (
    MockCreationEvent,
    MockDeletionEvent,
    MockResetEvent,
)
from .enhanced_shlex import AdvancedToken
from .shlex import ShlexTokenIterator

DiscoveryItem = Union[DiscoveryEvent, AdvancedToken]


class DiscoveryTokenIterator:
    """Iterates over tokens and yields discovery events or raw tokens."""

    def __init__(self, content: str, posix: bool = True) -> None:
        self.content = content
        self.iterator = ShlexTokenIterator(content, posix=posix)
        self.brace_depth = 0
        self.function_stack: List[Tuple[str, int]] = []

        # State machine variables
        self.pending_function_name: Union[str, None] = None
        self.pending_mock_op: Union[str, None] = None
        self.last_token: Union[AdvancedToken, None] = None

    def __iter__(self) -> Iterator[DiscoveryItem]:
        for token in self.iterator:
            # 1. Track brace depth and function endings
            if hasattr(token, "is_fully_quoted") and not token.is_fully_quoted:
                if "{" in token.unquoted_specials:
                    for _ in range(token.count("{")):
                        self.brace_depth += 1
                        if self.pending_function_name:
                            yield FunctionStartEvent(
                                self.pending_function_name, token.start_offset
                            )
                            self.function_stack.append(
                                (self.pending_function_name, self.brace_depth)
                            )
                            self.pending_function_name = None

                if "}" in token.unquoted_specials:
                    for _ in range(token.count("}")):
                        if (
                            self.function_stack
                            and self.function_stack[-1][1] == self.brace_depth
                        ):
                            name, _ = self.function_stack.pop()
                            yield FunctionEndEvent(name, token.end_offset)
                        self.brace_depth -= 1

            # 2. Check for 'function' keyword
            if not token.is_fully_quoted and token == "function":
                self.pending_function_name = "PENDING_KEYWORD"
                yield token
                self.last_token = token
                continue

            if self.pending_function_name == "PENDING_KEYWORD":
                self.pending_function_name = str(token)
                yield token
                self.last_token = token
                continue

            # 3. Check for name followed by ()
            if (
                not token.is_fully_quoted
                and token == "()"
                and self.last_token
                and not self.last_token.is_fully_quoted
            ):
                self.pending_function_name = str(self.last_token)

            # 4. Check for mock events
            if not token.is_fully_quoted:
                if token == "_mock.create":
                    self.pending_mock_op = "create"
                    yield token
                    self.last_token = token
                    continue
                elif token == "_mock.delete":
                    self.pending_mock_op = "delete"
                    yield token
                    self.last_token = token
                    continue
                elif token == "_mock.reset_all":
                    yield token
                    yield MockResetEvent(token.start_offset)
                    self.last_token = token
                    continue

            # Handle pending mock ops
            if self.pending_mock_op:
                if self.pending_mock_op == "create":
                    yield MockCreationEvent(str(token), token.end_offset)
                elif self.pending_mock_op == "delete":
                    yield MockDeletionEvent(str(token), token.start_offset)
                self.pending_mock_op = None
                yield token
                self.last_token = token
                continue

            # 5. Default: yield the token itself
            yield token
            self.last_token = token
