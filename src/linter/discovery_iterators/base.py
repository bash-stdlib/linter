"""Base class for linter discovery iterators."""

import abc
from enum import Enum, auto
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from linter.state.file_state import FileLinterState
    from linter.state.global_state import GlobalLinterState
    from linter.token_iterators.enhanced_shlex import AdvancedToken


class DiscoveryAction(Enum):
    """Actions returned by discovery iterators to control the pipeline."""

    CONTINUE = auto()
    """Continue processing this token with the next iterator."""

    STOP_TOKEN = auto()
    """Stop processing this token and move to the next one."""

    STOP_LINE = auto()
    """Stop processing this line and skip to the next newline."""


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
    def handle_token(self, token: "AdvancedToken") -> "DiscoveryAction":
        """Process a single token and update the linter state.

        Returns:
            bool: True if processing should continue to the next iterator,
                  False otherwise.

        """
        pass
