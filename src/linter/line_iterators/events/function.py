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

    name: str
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
        except Exception:
            return

        for token_str in tokens:
            if not isinstance(token_str, AdvancedToken):
                continue
            token: AdvancedToken = token_str

            if not token.is_fully_quoted:
                # Handle braces for body scoping
                if (
                    token == self.OPEN_BRACE
                    and self.OPEN_BRACE in token.unquoted_specials
                ):
                    self.current_balance += 1
                    if self.pending:
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
                    continue

                if (
                    token == self.CLOSE_BRACE
                    and self.CLOSE_BRACE in token.unquoted_specials
                ):
                    if (
                        self.brace_stack
                        and self.current_balance == self.brace_stack[-1]
                    ):
                        scope = self.open_scopes.pop()
                        scope.end_line = line_num
                        scope.end_offset = offset + token.end_offset
                        self.brace_stack.pop()
                    self.current_balance -= 1
                    continue

                # Check for function definition signatures
                if token == self.FUNCTION_KEYWORD:
                    self.in_function_keyword = True
                    self.pending = None
                    # We don't have the name yet, but we have the start offset
                    # of 'function'. Actually, the requirement might be the
                    # name's offset or keyword's. Let's keep the keyword's
                    # for now as a reference point.
                    self._mark_potential_function(
                        None, line_num, offset + token.start_offset
                    )
                    continue

                if token in self.PARENS:
                    if not self.in_function_keyword and self.last_token:
                        self.pending = PendingFunction(
                            name=self.last_token,
                            line=line_num,
                            offset=offset + self.last_token.start_offset,
                        )
                    continue

                # It's a word
                if self.in_function_keyword and (
                    not self.pending or self.pending.name is None
                ):
                    self._mark_potential_function(
                        token,
                        line_num,
                        self.pending.offset
                        if self.pending
                        else offset + token.start_offset,
                    )

                self.last_token = token
            else:
                self.last_token = None

    def _mark_potential_function(
        self, name: Optional[str], line: int, offset: int
    ) -> None:
        self.pending = PendingFunction(name=name, line=line, offset=offset)  # type: ignore
