"""Transformer for removing line continuations from Bash code."""

from .base import TransformerBase


class LineContinuationTransformer(TransformerBase):
    """Removes backslash-newline line continuations."""

    def transform(self, content: "str") -> "str":
        return content.replace("\\\n", " ")
