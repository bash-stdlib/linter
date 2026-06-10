"""Base class for all linter pipelines."""

import abc
from typing import TYPE_CHECKING, Generic, List, TypeVar

if TYPE_CHECKING:
    from linter.state.file_state import FileLinterState
    from linter.state.global_state import GlobalLinterState

ProcessorType = TypeVar("ProcessorType")


class BasePipeline(abc.ABC, Generic[ProcessorType]):
    """Abstract base class for linter pipelines.

    Provides a common structure for managing collections of processors
    (validators, iterators, etc.) and executing them in sequence.
    """

    def __init__(
        self,
        global_state: "GlobalLinterState",
        file_state: "FileLinterState",
    ) -> None:
        self.global_state = global_state
        self.file_state = file_state
        self.processors: List[ProcessorType] = []

    @abc.abstractmethod
    def execute(self) -> None:
        """Execute the pipeline with its processors."""
        pass
