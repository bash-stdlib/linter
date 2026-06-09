from typing import TYPE_CHECKING, Any, Dict, List, Set

from mock.manager import MockManager

if TYPE_CHECKING:
    from parsers.token_iterators.discovery_events.base import DiscoveryEvent


class LinterState:
    """Encapsulates the current state of the linter during a run."""

    def __init__(self, metadata: Any) -> None:
        self.base_functions: Set[str] = set(metadata["functions"].keys())
        self.base_namespaces: Set[str] = set(metadata["namespaces"])
        self.base_metadata: Dict[str, Any] = metadata["functions"]

        self.functions: Set[str] = self.base_functions.copy()
        self.namespaces: Set[str] = self.base_namespaces.copy()
        self.metadata: Dict[str, Any] = self.base_metadata.copy()

        self.mock_manager = MockManager(self.base_metadata)
        self.current_absolute_offset: int = 0
        self.event_log: List["DiscoveryEvent"] = []

    def reset(self) -> None:
        """Reset state to base metadata."""
        self.functions = self.base_functions.copy()
        self.namespaces = self.base_namespaces.copy()
        self.metadata = self.base_metadata.copy()

    def clear(self) -> None:
        """Completely clear state for a new file."""
        self.reset()
        self.mock_manager.clear()
        self.event_log = []
