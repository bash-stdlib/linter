"""Base class for content transformers."""

import abc


class TransformerBase(abc.ABC):
    """Abstract base class for all transformers."""

    @abc.abstractmethod
    def transform(self, content: "str") -> "str":
        """Transform the given content and return the result."""
        pass
