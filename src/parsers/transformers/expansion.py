"""Transformer for simplifying Bash expansions for easier parsing."""

from typing import Dict, List, Tuple

from .base import TransformerBase


class ExpansionTransformer(TransformerBase):
    """Simplifies arithmetic and parameter expansions."""

    EXPANSION_CONFIG: "Dict[str, Tuple[str, str]]" = {
        "${": ("}", "${X}"),
        "$((": ("))", "$((X))"),
    }

    def transform(self, content: "str") -> "str":
        result: List[str] = []
        i = 0
        while i < len(content):
            matched = False
            for start_token, (end_token, placeholder) in self.EXPANSION_CONFIG.items():
                if content.startswith(start_token, i):
                    simplified, next_i = self._simplify_expansion(
                        content, i, start_token, end_token, placeholder
                    )
                    result.append(simplified)
                    i = next_i
                    matched = True
                    break

            if not matched:
                result.append(content[i])
                i += 1

        return "".join(result)

    def _simplify_expansion(
        self,
        content: "str",
        start_index: "int",
        start_token: "str",
        end_token: "str",
        placeholder: "str",
    ) -> "Tuple[str, int]":
        """Finds a matching expansion and returns the placeholder and next index."""
        count = 1
        j = start_index + len(start_token)
        while j <= len(content) - len(end_token) and count > 0:
            if content.startswith(start_token, j):
                count += 1
                j += len(start_token)
            elif content.startswith(end_token, j):
                count -= 1
                j += len(end_token)
            else:
                j += 1

        if count == 0:
            return placeholder, j

        return content[start_index], start_index + 1
