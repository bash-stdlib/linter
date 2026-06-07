"""Asset metadata for linter subshell tests."""

METADATA = {
    "functions": {
        "stdlib.echo": {
            "name": "stdlib.echo",
            "min_args": 1,
            "max_args": -1,
        },
        "stdlib.some.command": {
            "name": "stdlib.some.command",
            "min_args": 2,
            "max_args": 2,
        }
    },
    "namespaces": ["stdlib"],
}
