"""Cache-related exception: Empty cache."""

from .base import BaseLinterException


class EmptyCacheError(BaseLinterException):
    """Raised when the cache is empty and cannot be populated."""

    pass
