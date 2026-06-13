"""Discovery iterator for identifying mock lifecycles."""

from typing import TYPE_CHECKING, Optional

from linter.discovery_iterators.base import DiscoveryAction, DiscoveryIteratorBase

if TYPE_CHECKING:
    from linter.enhanced_shlex import AdvancedToken
    from linter.state.file_state import FileLinterState
    from linter.state.global_state import GlobalLinterState


class MockDiscoveryIterator(DiscoveryIteratorBase):
    """Tracks the instantiation and destruction of mocks to manage their active lifecycles."""

    CREATE_MOCK = "_mock.create"
    DELETE_MOCK = "_mock.delete"

    def __init__(
        self,
        global_state: "GlobalLinterState",
        file_state: "FileLinterState",
    ) -> None:
        super().__init__(global_state, file_state)
        self.last_token: Optional["AdvancedToken"] = None

    def handle_token(self, token: "AdvancedToken") -> DiscoveryAction:
        """Process tokens to find mock creation and deletion."""
        if token.is_fully_quoted:
            self.last_token = None
            return DiscoveryAction.CONTINUE

        if self.last_token == self.CREATE_MOCK:
            self._handle_create(token)
        elif self.last_token == self.DELETE_MOCK:
            self._handle_delete(token)

        self.last_token = token
        return DiscoveryAction.CONTINUE

    def _handle_create(self, token: "AdvancedToken") -> None:
        name = str(token)
        # We need to use start_offset of the name token
        self.file_state.add_mock_lifecycle(name, token.start_offset)

    def _handle_delete(self, token: "AdvancedToken") -> None:
        name = str(token)
        self.file_state.end_mock_lifecycle(name, token.start_offset)
