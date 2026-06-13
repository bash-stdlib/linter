"""Transformer for simplifying Bash expansions for easier parsing."""

from typing import Dict, List, NamedTuple, Tuple

from constants import ARRAY_EXPANSION_PLACEHOLDER
from .base import TransformerBase


class ExpansionConfig(NamedTuple):
    """Configuration for a specific type of shell expansion."""

    start_token: str
    end_token: str
    placeholder: str


class ExpansionTransformer(TransformerBase):
    """Simplifies arithmetic, parameter and subshell expansions."""

    # Note: Order is important. "arithmetic" must be defined before "subshell"
    # because "$(( " starts with "$(".
    EXPANSION_CONFIG: "Dict[str, ExpansionConfig]" = {
        "parameter": ExpansionConfig("${", "}", "${X}"),
        "arithmetic": ExpansionConfig("$((", "))", "$((X))"),
        "subshell": ExpansionConfig("$(", ")", "$(X)"),
    }

    def transform(self, content: "str") -> "str":
        result: List[str] = []
        i = 0
        while i < len(content):
            found_config = None
            for config in self.EXPANSION_CONFIG.values():
                if content.startswith(config.start_token, i):
                    found_config = config
                    break

            if found_config:
                simplified, next_i = self._simplify_expansion(content, i, found_config)
                result.append(simplified)
                i = next_i
            else:
                result.append(content[i])
                i += 1

        return "".join(result)

    def _simplify_expansion(
        self,
        content: "str",
        start_index: "int",
        config: "ExpansionConfig",
    ) -> "Tuple[str, int]":
        """Find a matching expansion and returns the placeholder and next index."""
        count = 1
        j = start_index + len(config.start_token)
        while j <= len(content) - len(config.end_token) and count > 0:
            nested_config = None
            for c in self.EXPANSION_CONFIG.values():
                if content.startswith(c.start_token, j):
                    nested_config = c
                    break

            if nested_config:
                if nested_config.start_token == config.start_token:
                    count += 1
                    j += len(nested_config.start_token)
                else:
                    # Different expansion type: skip its entire content recursively
                    # to avoid matching false end tokens.
                    _, next_j = self._simplify_expansion(content, j, nested_config)
                    j = next_j
            elif content.startswith(config.end_token, j):
                count -= 1
                j += len(config.end_token)
            else:
                j += 1

        if count == 0:
            full_expansion = content[start_index:j]
            if config.start_token == "${":
                if "[@]}" in full_expansion or "[*]}" in full_expansion:
                    return ARRAY_EXPANSION_PLACEHOLDER, j
                if full_expansion in ("${@}", "${*}"):
                    return ARRAY_EXPANSION_PLACEHOLDER, j

            return config.placeholder, j

        return content[start_index], start_index + 1
