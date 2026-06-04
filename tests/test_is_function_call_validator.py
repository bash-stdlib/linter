import unittest
from errors.std001 import STD001
from errors.std002 import STD002
from errors.std004 import STD004
from validators.is_function_call import IsFunctionCallValidator

class TestIsFunctionCallValidator(unittest.TestCase):
    def setUp(self) -> None:
        self.functions = {"stdlib.string.join", "stdlib.array.push"}
        self.namespaces = {"stdlib", "stdlib.string", "stdlib.array"}
        self.validator = IsFunctionCallValidator(self.functions, self.namespaces)

    def test_check__valid_function__returns_none(self) -> None:
        call = "stdlib.string.join"

        result = self.validator.check(call, "test.sh", 1, 1)

        self.assertIsNone(result)

    def test_check__misspelled_function__returns_std002(self) -> None:
        call = "stdlib.string.jin"

        result = self.validator.check(call, "test.sh", 1, 1)

        self.assertIsInstance(result, STD002)
        self.assertEqual(result.match, "stdlib.string.jin")

    def test_check__invalid_namespace__returns_std001(self) -> None:
        call = "stdlib.unknown.func"

        result = self.validator.check(call, "test.sh", 1, 1)

        self.assertIsInstance(result, STD001)
        self.assertEqual(result.namespace, "stdlib.unknown")

    def test_check__completely_unknown__returns_std004(self) -> None:
        self.validator.namespaces.remove("stdlib")
        call = "stdlib.unknown"

        result = self.validator.check(call, "test.sh", 1, 1)

        self.assertIsInstance(result, STD004)
