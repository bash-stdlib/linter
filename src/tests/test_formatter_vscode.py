import json
import unittest

from issues.errors.STD003 import STD003
from formatters.vscode_formatter import VSCodeFormatterBase


class TestVSCodeFormatterBase(unittest.TestCase):
    def setUp(self) -> None:
        self.formatter = VSCodeFormatterBase()

    def test_format__single_issue__returns_vscode_json(self) -> None:
        issue = STD003("test.sh", 5, 10, "stdlib.ns")

        result = self.formatter.format([issue])

        data = json.loads(result)
        self.assertEqual(len(data), 1)
        diag = data[0]
        self.assertEqual(diag["range"]["start"]["line"], 4)
        self.assertEqual(diag["range"]["start"]["character"], 9)
        self.assertEqual(diag["severity"], 1)
        self.assertEqual(diag["code"], "STD003")
        self.assertEqual(diag["source"], "bash-stdlib-lint")
        self.assertEqual(diag["file"], "test.sh")


if __name__ == "__main__":
    unittest.main()
