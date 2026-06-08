from typing import Optional


class FunctionScope:
    def __init__(
        self, name: str, start_offset: int, end_offset: Optional[int] = None
    ) -> None:
        self.name = name
        self.start_offset = start_offset
        self.end_offset = end_offset

    def is_inside(self, offset: int) -> bool:
        if self.end_offset is None:
            return offset >= self.start_offset
        return self.start_offset <= offset <= self.end_offset
