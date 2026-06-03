import unittest
from models import LinterError, ErrorCode

class TestModels(unittest.TestCase):
    def test_linter_error__to_dict__returns_correct_dictionary(self):
        error = LinterError(
            code=ErrorCode.STD001.name,
            file="test.sh",
            line=10,
            column=5,
            message="Error message",
            match="stdlib.match"
        )

        result = error.to_dict()

        self.assertEqual(result["code"], "STD001")
        self.assertEqual(result["file"], "test.sh")
        self.assertEqual(result["line"], 10)
        self.assertEqual(result["column"], 5)
        self.assertEqual(result["message"], "Error message")
        self.assertEqual(result["match"], "stdlib.match")

if __name__ == "__main__":
    unittest.main()
