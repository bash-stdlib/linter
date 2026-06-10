"""Base class for linter discovery iterators."""

import abc
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from linter.state.file_state import FileLinterState
    from linter.state.global_state import GlobalLinterState
    from parsers.token_iterators.enhanced_shlex import AdvancedToken


class DiscoveryIteratorBase(abc.ABC):
    """Abstract base class for iterators that process tokens for discovery."""

    def __init__(
        self,
        global_state: "GlobalLinterState",
        file_state: "FileLinterState",
    ) -> None:
        self.global_state = global_state
        self.file_state = file_state

    @abc.abstractmethod
    def handle_token(self, token: "AdvancedToken") -> bool:
        """Process a single token and update the linter state.

        Returns:
            bool: True if processing should continue to the next iterator,
                  False otherwise.

        """
        pass
