class BaseLinterError(Exception):
    """Base class for linter errors."""
    pass

class EmptyCacheError(BaseLinterError):
    """Raised when the cache is empty and cannot be populated."""
    pass
