"""Transformer for simplifying Bash expansions for easier parsing."""

from typing import List, Tuple

from .base import TransformerBase


class ExpansionTransformer(TransformerBase):
    """Simplifies arithmetic and parameter expansions."""

    PARAM_START = "${"
    PARAM_END = "}"
    ARITH_START = "$(("
    ARITH_END = "))"
    PLACEHOLDER_PARAM = "${X}"
    PLACEHOLDER_ARITH = "$((X))"

    def transform(self, content: "str") -> "str":
        result: List[str] = []
        i = 0
        while i < len(content):
            if content.startswith(self.PARAM_START, i):
                simplified, next_i = self._simplify_expansion(
                    content, i, self.PARAM_START, self.PARAM_END, self.PLACEHOLDER_PARAM
                )
                result.append(simplified)
                i = next_i
            elif content.startswith(self.ARITH_START, i):
                simplified, next_i = self._simplify_expansion(
                    content, i, self.ARITH_START, self.ARITH_END, self.PLACEHOLDER_ARITH
                )
                result.append(simplified)
                i = next_i
            else:
                result.append(content[i])
                i += 1
        return "".join(result)

    def _simplify_expansion(
        self, content: str, start_index: int, start_token: str, end_token: str, placeholder: str
    ) -> Tuple[str, int]:
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
