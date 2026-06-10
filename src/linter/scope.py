"""Module for tracking function scopes in Bash scripts."""



class FunctionScope:
    """Represents the scope of a Bash function."""

    def __init__(
        self,
        name: str,
        start_line: int,
        start_offset: int,
        end_line: int = -1,
        end_offset: int = -1,
    ) -> None:
        self.name = name
        self.start_line = start_line
        self.start_offset = start_offset
        self.end_line = end_line
        self.end_offset = end_offset

    def contains(self, line_num: int, offset: int) -> bool:
        """Check if a given coordinate falls within the function's scope."""
        if self.end_line == -1:
            # Function scope is still open, assume it goes to the end of the file
            if line_num < self.start_line:
                return False
            if line_num == self.start_line:
                return offset >= self.start_offset
            return True

        if line_num < self.start_line or line_num > self.end_line:
            return False

        if line_num == self.start_line:
            if line_num == self.end_line:
                # Same line start and end
                return self.start_offset <= offset <= self.end_offset
            return offset >= self.start_offset

        if line_num == self.end_line:
            return offset <= self.end_offset

        return True

    def __repr__(self) -> str:
        return (
            f"FunctionScope(name={self.name!r}, "
            f"start={self.start_line}:{self.start_offset}, "
            f"end={self.end_line}:{self.end_offset})"
        )
