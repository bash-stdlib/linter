"""Asset metadata for linter edge cases tests."""

METADATA = {
    "functions": {
        "stdlib.foo": {
            "name": "stdlib.foo",
            "min_args": 0,
            "max_args": 0,
        },
        "stdlib.bar": {
            "name": "stdlib.bar",
            "min_args": 1,
            "max_args": 1,
        },
    },
    "namespaces": ["stdlib"],
}

SCRIPTS = {
    "function_definitions": "function stdlib.foo() {\n  echo hello\n}\nstdlib.foo () {\n  echo hi\n}",
    "function_as_argument": "echo stdlib.foo",
    "assignment": "VAR=stdlib.foo",
    "line_continuation": "stdlib.bar \\\n  arg1",
    "nested_complex_subshell": 'nested="${HELLO:-"$(stdlib.foo)"}"',
    "namespace_and_function_ambiguity": "stdlib.foo",
}
