import json
import unittest

from errors.std003 import STD003
from errors.std008 import STD008
from formatters.vscode_formatter import VSCodeFormatterBase


class TestVSCodeFormatterBase(unittest.TestCase):
    def setUp(self) -> None:
        self.formatter = VSCodeFormatterBase()

    def test_format__single_error__returns_vscode_json(self) -> None:
        error = STD003("test.sh", 5, 10, "stdlib.ns")

        result = self.formatter.format([error])

        data = json.loads(result)
        self.assertEqual(len(data), 1)
        diag = data[0]
        self.assertEqual(diag["range"]["start"]["line"], 4)  # 0-indexed
        self.assertEqual(diag["range"]["start"]["character"], 9)  # 0-indexed
        self.assertEqual(diag["severity"], 1)  # Error
        self.assertEqual(diag["code"], "STD003")
        self.assertEqual(diag["source"], "bash-stdlib-lint")
        self.assertEqual(diag["file"], "test.sh")

    def test_format__single_warning__returns_vscode_json_with_warning_severity(
        self,
    ) -> None:
        error = STD008("test.sh", 1, 1, "STD001")

        result = self.formatter.format([error])

        data = json.loads(result)
        self.assertEqual(len(data), 1)
        diag = data[0]
        self.assertEqual(diag["severity"], 2)  # Warning
        self.assertEqual(diag["code"], "STD008")


if __name__ == "__main__":
    unittest.main()
