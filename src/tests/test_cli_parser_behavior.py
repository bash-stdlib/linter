import unittest

from cli import get_parser


class TestCLIParserBehavior(unittest.TestCase):
    def test_get_parser__multiple_flags_and_files__parses_correctly(self) -> None:
        parser = get_parser()

        args = parser.parse_args(
            ["check", "-i", "C1", "-i", "C2", "-a", "A1", "f1", "f2"]
        )

        self.assertEqual(args.ignore, ["C1", "C2"])
        self.assertEqual(args.appendum, ["A1"])
        self.assertEqual(args.files, ["f1", "f2"])

    def test_get_parser__zero_files_provided__raises_system_exit(self) -> None:
        parser = get_parser()

        with self.assertRaises(SystemExit):
            parser.parse_args(["check", "-i", "C1"])

    def test_get_parser__interleaved_flags_at_end__parses_correctly(self) -> None:
        parser = get_parser()

        args = parser.parse_args(["check", "f1", "f2", "-i", "C1"])

        self.assertEqual(args.ignore, ["C1"])
        self.assertEqual(args.files, ["f1", "f2"])


if __name__ == "__main__":
    unittest.main()
