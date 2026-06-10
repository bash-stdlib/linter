import unittest
from cli import get_parser

class TestCLIParserBehavior(unittest.TestCase):
    def test_parser_configuration(self) -> None:
        parser = get_parser()

        # Test case: multiple flags and multiple files
        args = parser.parse_args(["check", "-i", "C1", "-i", "C2", "-a", "A1", "f1", "f2"])

        self.assertEqual(args.ignore, ["C1", "C2"])
        self.assertEqual(args.appendum, ["A1"])
        self.assertEqual(args.files, ["f1", "f2"])

    def test_parser_configuration__requires_one_file(self) -> None:
        parser = get_parser()

        with self.assertRaises(SystemExit):
            # Should fail because nargs="+" requires at least one file
            parser.parse_args(["check", "-i", "C1"])

    def test_parser_configuration__interleaved_flags_at_end(self) -> None:
        parser = get_parser()

        args = parser.parse_args(["check", "f1", "f2", "-i", "C1"])

        self.assertEqual(args.ignore, ["C1"])
        self.assertEqual(args.files, ["f1", "f2"])

if __name__ == "__main__":
    unittest.main()
