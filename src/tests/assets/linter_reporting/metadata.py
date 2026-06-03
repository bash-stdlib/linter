"""Asset metadata for linter reporting tests."""

METADATA = {
    "functions": {
        "stdlib.array.assert.is_array": {
            "name": "stdlib.array.assert.is_array",
            "arguments": ["$1"],
            "min_args": 1,
            "max_args": 1,
        },
    },
    "namespaces": [
        "stdlib",
        "stdlib.array",
        "stdlib.array.assert",
    ],
}
