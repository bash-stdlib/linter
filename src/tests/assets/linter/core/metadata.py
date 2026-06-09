"""Asset metadata for core linter tests."""

METADATA = {
    "functions": {
        "stdlib.array.assert.is_array": {
            "name": "stdlib.array.assert.is_array",
            "arguments": ["$1"],
            "keywords": [],
            "globals": [],
            "min_args": 1,
            "max_args": 1,
        },
        "stdlib.string.args.join": {
            "name": "stdlib.string.args.join",
            "arguments": ["$1", "..."],
            "keywords": [],
            "globals": [],
            "min_args": 1,
            "max_args": -1,
        },
    },
    "namespaces": [
        "stdlib",
        "stdlib.array",
        "stdlib.array.assert",
        "stdlib.string",
        "stdlib.string.args",
    ],
}
