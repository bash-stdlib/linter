import unittest
from unittest.mock import MagicMock, patch

from cli.commands.list import ListErrorCodesCommand


class TestListErrorCodesCommand(unittest.TestCase):
    def test_execute__always__prints_codes_and_titles(self) -> None:
        command = ListErrorCodesCommand()

        with patch("builtins.print") as mock_print:
            command.execute(MagicMock())

            output = "\n".join(
                str(call.args[0]) for call in mock_print.call_args_list if call.args
            )
            self.assertIn("STD001", output)
            self.assertIn("invalid namespace", output)


if __name__ == "__main__":
    unittest.main()
