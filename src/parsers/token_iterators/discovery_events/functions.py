from typing import TYPE_CHECKING

from functions.scope import FunctionScope
from .base import DiscoveryEvent

if TYPE_CHECKING:
    from linter import Linter
    from mock.manager import MockManager


class FunctionStartEvent(DiscoveryEvent):
    def __init__(self, name: str, offset: int) -> None:
        super().__init__(offset)
        self.name = name

    def handle(self, linter: "Linter") -> None:
        linter.mock_manager.set_function_scopes(
            linter.mock_manager.function_scopes
            + [FunctionScope(self.name, self.offset)]
        )

    def handle_pre_scan(self, mock_manager: "MockManager") -> None:
        mock_manager.set_function_scopes(
            mock_manager.function_scopes + [FunctionScope(self.name, self.offset)]
        )


class FunctionEndEvent(DiscoveryEvent):
    def __init__(self, name: str, offset: int) -> None:
        super().__init__(offset)
        self.name = name

    def handle(self, linter: "Linter") -> None:
        for scope in reversed(linter.mock_manager.function_scopes):
            if scope.name == self.name and scope.end_offset is None:
                scope.end_offset = self.offset
                break

    def handle_pre_scan(self, mock_manager: "MockManager") -> None:
        for scope in reversed(mock_manager.function_scopes):
            if scope.name == self.name and scope.end_offset is None:
                scope.end_offset = self.offset
                break
