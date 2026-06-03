import json
import unittest

from errors.std003 import STD003
from formatters.vscode_formatter import VSCodeFormatter


class TestVSCodeFormatter(unittest.TestCase):
    def setUp(self) -> None:
        self.formatter = VSCodeFormatter()

    def test_format__single_issue__returns_vscode_json(self) -> None:
        issue = STD003("test.sh", 5, 10, "stdlib.ns")

        result = self.formatter.format([issue])

        data = json.loads(result)
        self.assertEqual(len(data), 1)
        diag = data[0]
        self.assertEqual(diag["range"]["start"]["line"], 4)  # 0-indexed
        self.assertEqual(diag["range"]["start"]["character"], 9)  # 0-indexed
        self.assertEqual(diag["code"], "STD003")
        self.assertEqual(diag["source"], "bash-stdlib-lint")


if __name__ == "__main__":
    unittest.main()
