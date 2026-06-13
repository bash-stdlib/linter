"""Asset metadata for mock linter tests."""

METADATA = {
    "functions": {
        "stdlib.io.print": {
            "name": "stdlib.io.print",
            "min_args": 1,
            "max_args": -1,
        },
        "_mock.create": {
            "name": "_mock.create",
            "min_args": 1,
            "max_args": 1,
        },
        "_mock.delete": {
            "name": "_mock.delete",
            "min_args": 1,
            "max_args": 1,
        },
        "object.mock.assert_not_called": {
            "name": "object.mock.assert_not_called",
            "min_args": 0,
            "max_args": 0,
        },
        "object.mock.clear": {
            "name": "object.mock.clear",
            "min_args": 0,
            "max_args": 0,
        },
        "object.mock.assert_called_once_with": {
            "name": "object.mock.assert_called_once_with",
            "min_args": 1,
            "max_args": 1,
        }
    },
    "namespaces": ["stdlib", "stdlib.io", "_mock", "object", "object.mock"],
}

SCRIPTS = {
    "valid_global_mock": """_mock.create ls
ls.mock.assert_not_called
ls -la""",
    "mock_in_production": """_mock.create ls""",
    "inactive_mock": """_mock.create ls
_mock.delete ls
ls.mock.assert_not_called""",
    "sequential_mock_scope": """my_func() {
  _mock.create grep
  grep.mock.assert_not_called
}
grep.mock.assert_not_called""",
    "mock_stdlib_function": """_mock.create stdlib.io.print
stdlib.io.print "hello"
stdlib.io.print.mock.assert_not_called""",
    "invalid_mock_method": """_mock.create ls
ls.mock.invalid_method""",
    "mock_method_wrong_args": """_mock.create ls
ls.mock.assert_called_once_with""",
    "mock_custom_function": """_mock.create custom_func
custom_func "arg"
custom_func.mock.assert_called_once_with "arg\"""",
}
