"""Event for identifying Bash function starts and ends."""

from typing import TYPE_CHECKING, List, NamedTuple, Optional

from linter.line_iterators.events.base import EventBase
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


class FunctionEvent(EventBase):
    """Identifies Bash function starts and ends."""

    FUNCTION_KEYWORD = "function"
    OPEN_BRACE = "{"
    CLOSE_BRACE = "}"
    PARENS = ("(", ")", "()")

    def __init__(
        self, global_state: "GlobalLinterState", file_state: "FileLinterState"
    ) -> None:
        super().__init__(global_state, file_state)
        self.open_scopes: List[FunctionScope] = []
        self.brace_stack: List[int] = []
        self.current_balance = 0
        self.pending: Optional[PendingFunction] = None
        self.in_function_keyword = False
        self.last_token: Optional[AdvancedToken] = None

    def match(self, line_content: str) -> bool:
        """Evaluate if the content is a match."""
        return any(
            x in line_content for x in (self.FUNCTION_KEYWORD, "{", "}", "(", ")")
        )

    def handle(self, line_content: str, line_num: int, offset: int) -> None:
        try:
            tokens = list(ShlexTokenIterator(line_content))
        except ValueError:
            return

        for token_str in tokens:
            if not isinstance(token_str, AdvancedToken):
                continue
            token: AdvancedToken = token_str

            if not token.is_fully_quoted:
                if (
                    token == self.OPEN_BRACE
                    and self.OPEN_BRACE in token.unquoted_specials
                ):
                    self._handle_open_brace()
                    continue

                if (
                    token == self.CLOSE_BRACE
                    and self.CLOSE_BRACE in token.unquoted_specials
                ):
                    self._handle_close_brace(line_num, offset + token.end_offset)
                    continue

                if token == self.FUNCTION_KEYWORD:
                    self._handle_function_keyword(line_num, offset + token.start_offset)
                    continue

                if token in self.PARENS:
                    self._handle_parentheses(line_num, offset)
                    continue

                self._handle_word(token, line_num, offset)
                self.last_token = token
            else:
                self.last_token = None

    def _handle_open_brace(self) -> None:
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

    def _handle_close_brace(self, line_num: int, absolute_end_offset: int) -> None:
        if self.brace_stack and self.current_balance == self.brace_stack[-1]:
            scope = self.open_scopes.pop()
            scope.end_line = line_num
            scope.end_offset = absolute_end_offset
            self.brace_stack.pop()
        self.current_balance -= 1

    def _handle_function_keyword(
        self, line_num: int, absolute_start_offset: int
    ) -> None:
        self.in_function_keyword = True
        self.pending = None
        self._mark_potential_function(None, line_num, absolute_start_offset)

    def _handle_parentheses(self, line_num: int, line_offset: int) -> None:
        if not self.in_function_keyword and self.last_token:
            self.pending = PendingFunction(
                name=str(self.last_token),
                line=line_num,
                offset=line_offset + self.last_token.start_offset,
            )

    def _handle_word(
        self, token: AdvancedToken, line_num: int, line_offset: int
    ) -> None:
        if self.in_function_keyword and (not self.pending or self.pending.name is None):
            self._mark_potential_function(
                str(token),
                line_num,
                self.pending.offset
                if self.pending
                else line_offset + token.start_offset,
            )

    def _mark_potential_function(
        self, name: Optional[str], line: int, offset: int
    ) -> None:
        self.pending = PendingFunction(name=name, line=line, offset=offset)
