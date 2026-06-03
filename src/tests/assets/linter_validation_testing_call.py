"""Asset metadata for linter testing call validation tests."""

METADATA = {
    "stdlib.test.func": {"is_testing": True},
    "stdlib.prod.func": {"is_testing": False},
}

FUNCTIONS = {"stdlib.test.func", "stdlib.prod.func"}
NAMESPACES = {"stdlib.test", "stdlib.prod"}
