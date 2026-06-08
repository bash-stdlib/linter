from mock.manager import MockManager
from parsers.token_iterators.functions import FunctionDefinitionsTokenIterator
from parsers.token_iterators.mock_events import MockEventsTokenIterator


class MockScanner:
    """Helper class to scan Bash content for function scopes and mock lifetimes."""

    def __init__(self, mock_manager: MockManager) -> None:
        self.mock_manager = mock_manager

    def scan_file(self, content: str) -> None:
        """Single-pass scan for both scopes and mock creations."""
        # We still need both for different purposes, but we can combine the
        # initial discovery
        scopes = list(FunctionDefinitionsTokenIterator(content))
        self.mock_manager.set_function_scopes(scopes)

        for event_type, mock_name, offset in MockEventsTokenIterator(content):
            if event_type == "create":
                self.mock_manager.create_mock(mock_name, offset)

    def track_mock_lifetimes(self, line_content: str, line_offset: int) -> None:
        """Sequentially track deletions and resets."""
        for event_type, mock_name, offset in MockEventsTokenIterator(line_content):
            absolute_offset = line_offset + offset
            if event_type == "delete":
                self.mock_manager.delete_mock(mock_name, absolute_offset)
            elif event_type == "reset_all":
                self.mock_manager.reset_all(absolute_offset)
