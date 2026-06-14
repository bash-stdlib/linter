"""Asset metadata for linter suppression tests."""

METADATA = {
    "functions": {
        "stdlib.array.assert.is_array": {
            "name": "stdlib.array.assert.is_array",
            "arguments": [{"name": "$1", "type": "string"}],
            "keywords": [],
            "globals": [],
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
