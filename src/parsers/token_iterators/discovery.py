"""Token-based discovery iterator for the bash-stdlib linter."""

from typing import TYPE_CHECKING, List, NamedTuple, Optional

from linter.scope import FunctionScope
from parsers.token_iterators.enhanced_shlex import AdvancedToken
from parsers.token_iterators.shlex import ShlexTokenIterator

if TYPE_CHECKING:
    from linter.state.file_state import FileLinterState
    from linter.state.global_state import GlobalLinterState


class PendingFunction(NamedTuple):
    """Temporary storage for a potential function definition."""

    name: Optional[str]
    line: int
    offset: int


class DiscoveryTokenIterator:
    """Iterates over tokens and dispatches discovery events."""

    FUNCTION_KEYWORD = "function"
    OPEN_BRACE = "{"
    CLOSE_BRACE = "}"
    PARENS = ("(", ")", "()")

    def __init__(
        self,
        content: str,
        global_state: "GlobalLinterState",
        file_state: "FileLinterState",
    ) -> None:
        self.tokens = ShlexTokenIterator(content)
        self.global_state = global_state
        self.file_state = file_state
        self.open_scopes: List[FunctionScope] = []
        self.brace_stack: List[int] = []
        self.current_balance = 0
        self.pending: Optional[PendingFunction] = None
        self.in_function_keyword = False
        self.last_token: Optional[AdvancedToken] = None

    def run(self) -> None:
        """Run the discovery pass."""
        try:
            for token_str in self.tokens:
                if not isinstance(token_str, AdvancedToken):
                    continue
                token: AdvancedToken = token_str
                self._handle_token(token)
        except ValueError:
            pass

    def _handle_token(self, token: AdvancedToken) -> None:
        if token.is_fully_quoted:
            self.last_token = None
            return

        if token == self.OPEN_BRACE and self.OPEN_BRACE in token.unquoted_specials:
            self._handle_open_brace(token)
        elif token == self.CLOSE_BRACE and self.CLOSE_BRACE in token.unquoted_specials:
            self._handle_close_brace(token)
        elif token == self.FUNCTION_KEYWORD:
            self._handle_function_keyword(token)
        elif token in self.PARENS:
            self._handle_parentheses(token)
        else:
            self._handle_word(token)
            self.last_token = token
            return

        self.last_token = token

    def _handle_open_brace(self, token: AdvancedToken) -> None:
        self.current_balance += 1
        if self.pending and self.pending.name:
            scope = FunctionScope(
                name=self.pending.name,
                start_line=self.pending.line,
                start_offset=self.pending.offset,
            )
            self.file_state.function_scopes.append(scope)
            self.open_scopes.append(scope)
            self.brace_stack.append(self.current_balance)
            self.pending = None
        self.in_function_keyword = False

    def _handle_close_brace(self, token: AdvancedToken) -> None:
        if self.brace_stack and self.current_balance == self.brace_stack[-1]:
            scope = self.open_scopes.pop()
            scope.end_line = token.line_num
            scope.end_offset = token.end_offset
            self.brace_stack.pop()
        self.current_balance -= 1

    def _handle_function_keyword(self, token: AdvancedToken) -> None:
        self.in_function_keyword = True
        self.pending = PendingFunction(
            name=None, line=token.line_num, offset=token.start_offset
        )

    def _handle_parentheses(self, token: AdvancedToken) -> None:
        if not self.in_function_keyword and self.last_token:
            self.pending = PendingFunction(
                name=str(self.last_token),
                line=self.last_token.line_num,
                offset=self.last_token.start_offset,
            )

    def _handle_word(self, token: AdvancedToken) -> None:
        if self.in_function_keyword and (not self.pending or self.pending.name is None):
            self.pending = PendingFunction(
                name=str(token),
                line=self.pending.line if self.pending else token.line_num,
                offset=self.pending.offset if self.pending else token.start_offset,
            )
