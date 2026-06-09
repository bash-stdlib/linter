import os
import unittest
from typing import Any

from linter import Linter


class TestFunctionScopes(unittest.TestCase):
    def setUp(self) -> None:
        metadata: Any = {"functions": {}, "namespaces": []}
        self.linter = Linter(metadata)
        self.asset_dir = os.path.join(
            os.path.dirname(__file__), "assets/linter/function_scopes"
        )

    def test_basic_function_scope(self) -> None:
        filepath = os.path.join(self.asset_dir, "basic.sh")

        self.linter.lint(filepath)
        scopes = self.linter.file_state.function_scopes
        self.assertEqual(len(scopes), 1)
        scope = scopes[0]
        self.assertEqual(scope.name, "func")
        self.assertEqual(scope.start_line, 1)
        self.assertTrue(scope.contains(2, 5))
        self.assertFalse(scope.contains(0, 0))
        self.assertFalse(scope.contains(4, 0))

    def test_function_keyword_scope(self) -> None:
        filepath = os.path.join(self.asset_dir, "keyword.sh")

        self.linter.lint(filepath)
        scopes = self.linter.file_state.function_scopes
        self.assertEqual(len(scopes), 1)
        scope = scopes[0]
        self.assertEqual(scope.name, "func")
        self.assertEqual(scope.start_line, 1)

    def test_nested_functions(self) -> None:
        filepath = os.path.join(self.asset_dir, "nested.sh")

        self.linter.lint(filepath)
        scopes = self.linter.file_state.function_scopes
        self.assertEqual(len(scopes), 2)

        outer = next(s for s in scopes if s.name == "outer")
        inner = next(s for s in scopes if s.name == "inner")

        self.assertTrue(outer.contains(3, 5))  # inside inner
        self.assertTrue(inner.contains(3, 5))
        self.assertTrue(outer.contains(6, 5))  # inside outer, but after inner
        self.assertFalse(inner.contains(6, 5))

    def test_unclosed_function_reports_error(self) -> None:
        filepath = os.path.join(self.asset_dir, "unclosed.sh")

        errors = self.linter.lint(filepath)
        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0].CODE, "STD009")

    def test_quoted_braces_ignored(self) -> None:
        filepath = os.path.join(self.asset_dir, "quoted_braces.sh")

        self.linter.lint(filepath)
        scopes = self.linter.file_state.function_scopes
        self.assertEqual(len(scopes), 1)
        self.assertEqual(scopes[0].end_line, 3)

    def test_shadowing_functions(self) -> None:
        filepath = os.path.join(self.asset_dir, "shadowing.sh")

        self.linter.lint(filepath)
        scopes = self.linter.file_state.function_scopes
        self.assertEqual(len(scopes), 2)

        outer = next(s for s in scopes if s.start_line == 1)
        inner = next(s for s in scopes if s.start_line == 2)

        self.assertEqual(outer.name, "hello")
        self.assertEqual(inner.name, "hello")

        self.assertTrue(outer.contains(3, 5))
        self.assertTrue(inner.contains(3, 5))
        self.assertTrue(outer.contains(5, 5))
        self.assertFalse(inner.contains(5, 5))


if __name__ == "__main__":
    unittest.main()
