import unittest
from transformers.expansion import ExpansionTransformer

class TestExpansionTransformer(unittest.TestCase):
    def setUp(self):
        self.transformer = ExpansionTransformer()

    def test_transform__arithmetic_expansion__simplifies_to_placeholder(self):
        content = "echo $((1 + 2))"

        result = self.transformer.transform(content)

        self.assertEqual(result, "echo $((X))")

    def test_transform__parameter_expansion__simplifies_to_placeholder(self):
        content = "echo ${VAR}"

        result = self.transformer.transform(content)

        self.assertEqual(result, "echo ${X}")

    def test_transform__nested_expansions__simplifies_non_greedily(self):
        content = "echo ${VAR} and ${OTHER}"

        result = self.transformer.transform(content)

        self.assertEqual(result, "echo ${X} and ${X}")

    def test_transform__complex_arithmetic__simplifies_non_greedily(self):
        content = "echo $((1 + 2)) and $((3 + 4))"

        result = self.transformer.transform(content)

        self.assertEqual(result, "echo $((X)) and $((X))")

if __name__ == "__main__":
    unittest.main()
