from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from linter import Linter
    from mock.manager import MockManager


class DiscoveryEvent:
    """Base class for all discovery events."""

    def __init__(self, offset: int) -> None:
        self.offset = offset

    def handle(self, linter: "Linter") -> None:
        """Handle the event within the linter context."""
        pass

    def handle_pre_scan(self, mock_manager: "MockManager") -> None:
        """Handle the event during the pre-scan pass."""
        pass
