"""Asset metadata for STD011 variadic tests."""

from tests.assets.linter.core.metadata import METADATA

STD011_METADATA = METADATA.copy()
STD011_METADATA["functions"] = METADATA["functions"].copy()
STD011_METADATA["functions"]["stdlib.test.variadic"] = {
    "name": "stdlib.test.variadic",
    "min_args": 1,
    "max_args": -1,
}
STD011_METADATA["functions"]["stdlib.test.strict"] = {
    "name": "stdlib.test.strict",
    "min_args": 1,
    "max_args": 1,
}
STD011_METADATA["functions"]["object.mock.assert_calls_are"] = {
    "name": "object.mock.assert_calls_are",
    "min_args": 0,
    "max_args": -1,
}
STD011_METADATA["functions"]["stdlib.test.optional"] = {
    "name": "stdlib.test.optional",
    "min_args": 1,
    "max_args": 3,
}
STD011_METADATA["namespaces"] = STD011_METADATA["namespaces"] + [
    "object",
    "object.mock",
]
