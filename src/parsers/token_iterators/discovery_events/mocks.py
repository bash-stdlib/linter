from typing import TYPE_CHECKING

from .base import DiscoveryEvent

if TYPE_CHECKING:
    from linter import Linter
    from mock.manager import MockManager


class MockCreationEvent(DiscoveryEvent):
    def __init__(self, name: str, offset: int) -> None:
        super().__init__(offset)
        self.name = name

    def handle(self, linter: "Linter") -> None:
        linter.mock_manager.create_mock(self.name, self.offset)

    def handle_pre_scan(self, mock_manager: "MockManager") -> None:
        mock_manager.record_discovered_name(self.name)


class MockDeletionEvent(DiscoveryEvent):
    def __init__(self, name: str, offset: int) -> None:
        super().__init__(offset)
        self.name = name

    def handle(self, linter: "Linter") -> None:
        linter.mock_manager.delete_mock(self.name, self.offset)


class MockResetEvent(DiscoveryEvent):
    def handle(self, linter: "Linter") -> None:
        linter.mock_manager.reset_all(self.offset)
