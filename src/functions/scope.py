class FunctionScope:
    def __init__(self, name: str, start_offset: int, end_offset: int) -> None:
        self.name = name
        self.start_offset = start_offset
        self.end_offset = end_offset

    def is_inside(self, offset: int) -> bool:
        return self.start_offset <= offset <= self.end_offset
