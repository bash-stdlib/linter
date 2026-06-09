"""Event for identifying Bash function starts and ends."""

from typing import TYPE_CHECKING, List, Optional

from linter.line_iterators.events.base import EventBase
from linter.scope import FunctionScope
from parsers.token_iterators.shlex import ShlexTokenIterator

if TYPE_CHECKING:
    from linter.state.file_state import FileLinterState
    from linter.state.global_state import GlobalLinterState
    from parsers.token_iterators.enhanced_shlex import AdvancedToken


class FunctionEvent(EventBase):
    """Identifies Bash function starts and ends."""

    def __init__(
        self, global_state: "GlobalLinterState", file_state: "FileLinterState"
    ) -> None:
        super().__init__(global_state, file_state)
        self.open_scopes: List[FunctionScope] = []
        self.brace_stack: List[int] = []
        self.current_balance = 0
        self.pending_function_name: Optional[str] = None
        self.pending_start_line: int = -1
        self.pending_start_offset: int = -1
        self.in_function_keyword = False
        self.last_token: Optional["AdvancedToken"] = None

    def match(self, line_content: str) -> bool:
        """Evaluate if the content is a match."""
        # Check for function keywords or parentheses that suggest a function definition
        # or braces that suggest scope changes.
        return any(x in line_content for x in ("function", "(", ")", "{", "}"))

    def handle(self, line_content: str, line_num: int, offset: int) -> None:
        try:
            tokens = list(ShlexTokenIterator(line_content))
        except Exception:
            return

        for token_str in tokens:
            from parsers.token_iterators.enhanced_shlex import AdvancedToken

            if not isinstance(token_str, AdvancedToken):
                continue
            token: AdvancedToken = token_str

            if not token.is_fully_quoted:
                # Handle braces for body scoping
                if token == "{" and "{" in token.unquoted_specials:
                    self.current_balance += 1
                    if self.pending_function_name:
                        scope = FunctionScope(
                            name=self.pending_function_name,
                            start_line=self.pending_start_line,
                            start_offset=self.pending_start_offset,
                        )
                        self.file_state.function_scopes.append(scope)
                        self.open_scopes.append(scope)
                        self.brace_stack.append(self.current_balance)
                        self.pending_function_name = None
                    self.in_function_keyword = False
                    continue

                if token == "}" and "}" in token.unquoted_specials:
                    if self.brace_stack and self.current_balance == self.brace_stack[-1]:
                        scope = self.open_scopes.pop()
                        scope.end_line = line_num
                        scope.end_offset = offset + token.end_offset
                        self.brace_stack.pop()
                    self.current_balance -= 1
                    continue

                # Check for function definition signatures
                if token == "function":
                    self.in_function_keyword = True
                    self.pending_function_name = None
                    self.pending_start_line = line_num
                    self.pending_start_offset = offset + token.start_offset
                    continue

                if token == "(" or token == "()":
                    if not self.in_function_keyword and self.last_token:
                        self.pending_function_name = self.last_token
                        self.pending_start_line = line_num
                        self.pending_start_offset = offset + self.last_token.start_offset
                    continue

                if token == ")":
                    continue

                # It's a word
                if self.in_function_keyword and not self.pending_function_name:
                    self.pending_function_name = token

                self.last_token = token
            else:
                self.last_token = None
