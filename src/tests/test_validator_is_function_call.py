"""Unit tests for the IsFunctionCallValidator."""

import unittest

from linter.state.file_state import FileLinterState
from linter.state.global_state import GlobalLinterState
from tests.assets.validator.is_function_call.metadata import METADATA
from validators.is_function_call import IsFunctionCallValidator


class TestIsFunctionCallValidator(unittest.TestCase):
    def setUp(self) -> None:
        self.global_state = GlobalLinterState(METADATA)
        self.file_state = FileLinterState()
        self.validator = IsFunctionCallValidator(self.global_state, self.file_state)

    def test_check__valid_function_call__returns_none(self) -> None:
        call = "stdlib.string.join"

        result = self.validator.check(call, "test.sh", 1, 1)

        self.assertIsNone(result)

    def test_check__misspelled_function__returns_std002(self) -> None:
        call = "stdlib.string.joinn"

        result = self.validator.check(call, "test.sh", 1, 1)

        assert result is not None
        self.assertEqual(result.CODE, "STD002")

    def test_check__invalid_namespace__returns_std001(self) -> None:
        call = "stdlib.unknown.func"

        result = self.validator.check(call, "test.sh", 1, 1)

        assert result is not None
        self.assertEqual(result.CODE, "STD001")

    def test_check__unknown_root__returns_std004(self) -> None:
        call = "unknown.func"

        result = self.validator.check(call, "test.sh", 1, 1)

        assert result is not None
        self.assertEqual(result.CODE, "STD004")

    def test_check__whitelisted_prefix__returns_none(self) -> None:
        call = "assert_custom_func"

        result = self.validator.check(call, "test.sh", 1, 1)

        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()
