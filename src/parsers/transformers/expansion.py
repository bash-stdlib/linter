"""Transformer for simplifying Bash expansions for easier parsing."""

from .base import TransformerBase


class ExpansionTransformer(TransformerBase):
    """Simplifies arithmetic and parameter expansions."""

    def transform(self, content: "str") -> "str":
        result = []
        i = 0
        while i < len(content):
            if content.startswith("${", i):
                # Start of a parameter expansion
                # Find matching } by counting braces
                count = 1
                j = i + 2
                while j < len(content) and count > 0:
                    if content.startswith("${", j):
                        count += 1
                        j += 2
                    elif content[j] == "}":
                        count -= 1
                        j += 1
                    else:
                        j += 1
                if count == 0:
                    result.append("${X}")
                    i = j
                else:
                    # Unbalanced, just append first char and move on
                    result.append(content[i])
                    i += 1
            elif content.startswith("$((", i):
                # Start of arithmetic expansion
                # Find matching )) by counting parentheses pairs
                count = 1
                j = i + 3
                while j < len(content) - 1 and count > 0:
                    if content.startswith("$((", j):
                        count += 1
                        j += 3
                    elif content.startswith("))", j):
                        count -= 1
                        j += 2
                    else:
                        j += 1
                if count == 0:
                    result.append("$((X))")
                    i = j
                else:
                    result.append(content[i])
                    i += 1
            else:
                result.append(content[i])
                i += 1
        return "".join(result)
