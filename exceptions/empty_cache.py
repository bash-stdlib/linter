"""Cache-related exception: Empty cache."""

from .base import BaseLinterException


class EmptyCacheError(BaseLinterException):
    """Raised when the cache is empty and cannot be populated."""

    def __init__(self, message="Cache is empty and failed to fetch documentation."):
        super().__init__(message)
