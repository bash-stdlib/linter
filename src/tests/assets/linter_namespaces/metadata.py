"""Asset metadata for namespace linter tests."""

METADATA = {
    "functions": {
        "stdlib.array.assert.is_array": {
            "name": "stdlib.array.assert.is_array",
            "arguments": ["$1"],
            "min_args": 1,
            "max_args": 1,
        },
        "_testing.func": {
            "name": "_testing.func",
            "arguments": [],
            "min_args": 0,
            "max_args": 0,
            "is_testing": True
        },
        "@parametrize.compose": {
            "name": "@parametrize.compose",
            "arguments": ["$1", "..."],
            "min_args": 1,
            "max_args": -1,
            "is_testing": True
        },
        "assert_rc": {
            "name": "assert_rc",
            "arguments": ["$1"],
            "min_args": 1,
            "max_args": 1,
            "is_testing": True
        }
    },
    "namespaces": [
        "stdlib",
        "stdlib.array",
        "stdlib.array.assert",
        "_testing",
        "_testing.example",
        "@parametrize"
    ],
}
