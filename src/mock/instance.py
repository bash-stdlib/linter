from typing import Optional

from functions.scope import FunctionScope


class MockInstance:
    def __init__(
        self, name: str, creation_offset: int, scope: Optional[FunctionScope]
    ) -> None:
        self.name = name
        self.creation_offset = creation_offset
        self.scope = scope
        self.deletion_offset: Optional[int] = None

    def is_active(self, offset: int) -> bool:
        if offset < self.creation_offset:
            return False
        if self.deletion_offset is not None and offset >= self.deletion_offset:
            return False
        if self.scope is None:
            return True
        return self.scope.is_inside(offset)
