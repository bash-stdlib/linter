"""Asset metadata for linter namespace call validation tests."""

FUNCTIONS = {"stdlib.string.join"}
NAMESPACES = {"stdlib", "stdlib.string"}

METADATA = {
    "functions": {f: {} for f in FUNCTIONS},
    "namespaces": NAMESPACES,
}
