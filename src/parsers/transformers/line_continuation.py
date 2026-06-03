"""Transformer for removing line continuations from Bash code."""

from .base import TransformerBase


class LineContinuationTransformer(TransformerBase):
    """Removes backslash-newline line continuations."""

    def transform(self, content: "str", preserve_lines: "bool" = False) -> "str":
        """Replace line continuations with vertical tabs or double spaces."""
        # Vertical tab (\v) preserves line counts without being a command separator.
        # Python's splitlines(True) treats \v as a line break.
        # shlex treats \v as a normal character (not whitespace by default),
        # but we will add it to whitespace in ShlexTokenIterator.
        replacement = " \v" if preserve_lines else "  "
        return content.replace("\\\n", replacement)
