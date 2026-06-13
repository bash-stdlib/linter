"""Module for tracking mock lifecycles in Bash scripts."""


class MockScope:
    """Represents the lifecycle of a mock object."""

    def __init__(
        self,
        name: str,
        start_offset: int,
        end_offset: int = -1,
    ) -> None:
        self.name = name
        self.start_offset = start_offset
        self.end_offset = end_offset

    def is_active(self, offset: int) -> bool:
        """Check if the mock is active at the given character offset."""
        if self.end_offset == -1:
            return offset >= self.start_offset

        return self.start_offset <= offset <= self.end_offset

    def __repr__(self) -> str:
        return "MockScope(name={!r}, start={}, end={})".format(
            self.name, self.start_offset, self.end_offset
        )
