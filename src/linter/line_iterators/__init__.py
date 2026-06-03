"""Line iterators for the linter."""

from .base import LineIteratorBase
from .comment_ignores import CommentIgnores

__all__ = ["LineIteratorBase", "CommentIgnores"]
