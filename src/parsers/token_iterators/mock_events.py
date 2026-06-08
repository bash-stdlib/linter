from typing import Iterator, Tuple

from .shlex import ShlexTokenIterator


class MockEventsTokenIterator:
    """Iterates over tokens to discover mock lifetime events."""

    def __init__(self, content: str) -> None:
        self.iterator = ShlexTokenIterator(content)

    def __iter__(self) -> Iterator[Tuple[str, str, int]]:
        """Yield lifetime events for mocks.

        Yields (event_type, mock_name, offset).
        """
        try:
            for token in self.iterator:
                if hasattr(token, "is_fully_quoted") and not token.is_fully_quoted:
                    if token == "_mock.create":
                        try:
                            mock_name = next(self.iterator)
                            yield ("create", mock_name, token.end_offset)
                        except StopIteration:
                            break
                    elif token == "_mock.delete":
                        try:
                            mock_name = next(self.iterator)
                            yield ("delete", mock_name, token.start_offset)
                        except StopIteration:
                            break
                    elif token == "_mock.reset_all":
                        yield ("reset_all", "", token.start_offset)
        except (StopIteration, ValueError):
            pass
