"""Transformer for simplifying Bash expansions for easier parsing."""

import re

from .base import TransformerBase


class ExpansionTransformer(TransformerBase):
    """Simplifies arithmetic and parameter expansions."""

    def transform(self, content: "str") -> "str":
        # Simplify $(( ... )) to $((X)) non-greedily
        content = re.sub(r"\$\(\(.*?\)\)", "$((X))", content)

        # Simplify ${ ... } to ${X} non-greedily
        content = re.sub(r"\${.*?}", "${X}", content)

        return content
