import unittest

from parsers.transformers.expansion import ExpansionTransformer


class TestExpansionTransformer(unittest.TestCase):
    def setUp(self) -> None:
        self.transformer = ExpansionTransformer()

    def test_transform__arithmetic_expansion__simplifies_to_placeholder(self) -> None:
        content = "echo $((1 + 2))"

        result = self.transformer.transform(content)

        # $((1 + 2)) is 11 chars. $((X)) is 7 chars. 4 spaces added.
        self.assertEqual(result, "echo $((X))    ")

    def test_transform__parameter_expansion__simplifies_to_placeholder(self) -> None:
        content = "echo ${VAR}"

        result = self.transformer.transform(content)

        # ${VAR} is 6 chars. ${X} is 4 chars. 2 spaces added.
        self.assertEqual(result, "echo ${X}  ")

    def test_transform__nested_expansions__simplifies_non_greedily(self) -> None:
        content = "echo ${VAR} and ${OTHER}"

        result = self.transformer.transform(content)

        # ${VAR} (6) -> ${X} (4) + 2 spaces
        # ${OTHER} (8) -> ${X} (4) + 4 spaces
        self.assertEqual(result, "echo ${X}   and ${X}    ")

    def test_transform__complex_arithmetic__simplifies_non_greedily(self) -> None:
        content = "echo $((1 + 2)) and $((3 + 4))"

        result = self.transformer.transform(content)

        self.assertEqual(result, "echo $((X))     and $((X))    ")

    def test_transform__nested_parameter_expansion__simplifies_fully(self) -> None:
        content = 'nested="${HELLO:-"${BYE}"}"'

        result = self.transformer.transform(content)

        # "${HELLO:-"${BYE}"}" is 21 chars. "${X}" is 5 chars. 16 spaces?
        # Wait, the content being transformed is starting at index 8: ${HELLO...}
        # length of ${HELLO:-"${BYE}"} is 18. ${X} is 4. 14 spaces.
        self.assertEqual(result, 'nested="${X}              "')

    def test_transform__nested_arithmetic_expansion__simplifies_fully(self) -> None:
        content = "echo $(( 1 + $(( 2 + 3 )) ))"

        result = self.transformer.transform(content)

        self.assertEqual(result, "echo $((X))                 ")

    def test_transform__subshell_in_parameter_expansion__simplifies_fully(self) -> None:
        content = 'nested="${HELLO:-"$(echo "}")"}"'

        result = self.transformer.transform(content)

        self.assertEqual(result, 'nested="${X}                   "')

    def test_transform__mixed_nesting__simplifies_fully(self) -> None:
        content = "echo $(echo $(( 1 + 2 )))"

        result = self.transformer.transform(content)

        self.assertEqual(result, "echo $(X)                ")


if __name__ == "__main__":
    unittest.main()
