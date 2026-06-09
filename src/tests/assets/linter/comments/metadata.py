"""Asset metadata for linter comments tests."""

METADATA = {
    "functions": {
        "stdlib.echo": {"min_args": 1, "max_args": 1},
        "stdlib.something": {"min_args": 0, "max_args": 0},
    },
    "namespaces": ["stdlib"],
}
