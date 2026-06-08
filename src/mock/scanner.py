
from mock.manager import MockManager
from parsers.token_iterators.discovery import DiscoveryTokenIterator
from parsers.token_iterators.discovery_events.functions import (
    FunctionEndEvent,
    FunctionStartEvent,
)
from parsers.token_iterators.discovery_events.mocks import (
    MockCreationEvent,
)


class MockScanner:
    """Helper class to scan Bash content for function scopes and mock lifetimes."""

    def __init__(self, mock_manager: MockManager) -> None:
        self.mock_manager = mock_manager

    def scan_file(self, content: str) -> None:
        """Single-pass scan for both scopes and mock creations."""
        discovery = DiscoveryTokenIterator(content)
        for item in discovery:
            if isinstance(
                item, (FunctionStartEvent, FunctionEndEvent, MockCreationEvent)
            ):
                item.handle_pre_scan(self.mock_manager)
