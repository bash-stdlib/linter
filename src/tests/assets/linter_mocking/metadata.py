METADATA = {
    "functions": {
        "stdlib.echo": {"name": "stdlib.echo", "min_args": 1, "max_args": 1},
        "object.mock.assert_called_once_with": {
            "name": "object.mock.assert_called_once_with",
            "min_args": 1,
            "max_args": 1,
            "is_mock_template": True,
        },
        "_mock.create": {
            "name": "_mock.create",
            "min_args": 1,
            "max_args": 1,
            "is_testing": True,
        },
        "_mock.delete": {
            "name": "_mock.delete",
            "min_args": 1,
            "max_args": 1,
            "is_testing": True,
        },
        "_mock.reset_all": {
            "name": "_mock.reset_all",
            "min_args": 0,
            "max_args": 0,
            "is_testing": True,
        },
    },
    "namespaces": ["stdlib", "object", "object.mock", "_mock"],
}
