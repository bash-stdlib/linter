"""Iterator that stops processing tokens when an unquoted comment is reached."""

from typing import Iterable, Iterator


class CommentsFilterTokenIterator:
    """Iterates over tokens and stops at the first unquoted '#' character."""

    def __init__(self, iterable: Iterable[str]) -> None:
        self.iterator = iter(iterable)
        self.stopped_at_comment = False

    def __iter__(self) -> Iterator[str]:
        return self

    def __next__(self) -> str:
        if self.stopped_at_comment:
            raise StopIteration

        token = next(self.iterator)
        if token == "#":
            self.stopped_at_comment = True
            raise StopIteration

        return token
