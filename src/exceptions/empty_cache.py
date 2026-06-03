"""Cache-related exception: Empty cache."""

from .base import BaseLinterException


class EmptyCacheError(BaseLinterException):
    """Raised when the cache is empty and cannot be populated."""

    def __init__(
        self, message: str = "Cache is empty and failed to fetch documentation."
    ) -> None:
        super().__init__(message)
