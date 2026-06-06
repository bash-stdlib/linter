import unittest
import os
from linter import Linter

class TestLinterAppendum(unittest.TestCase):
    def setUp(self):
        self.metadata = {
            "functions": {"stdlib.echo": {}},
            "namespaces": ["stdlib"]
        }

    def test_appendum_function(self):
        # Arrange
        linter = Linter(self.metadata, appendum=["stdlib.__message.get"])

        # Act
        with open("test_appendum.sh", "w") as f:
            f.write("stdlib.__message.get 'hello'\n")

        errors = linter.lint("test_appendum.sh")
        if os.path.exists("test_appendum.sh"):
            os.remove("test_appendum.sh")

        # Assert
        self.assertEqual(len(errors), 0)

    def test_appendum_namespace(self):
        # Arrange
        linter = Linter(self.metadata, appendum=["my_ns"])

        # Act
        with open("test_appendum_ns.sh", "w") as f:
            f.write("my_ns.foo 'bar'\n")

        errors = linter.lint("test_appendum_ns.sh")
        if os.path.exists("test_appendum_ns.sh"):
            os.remove("test_appendum_ns.sh")

        # Assert
        self.assertEqual(len(errors), 0)

    def test_appendum_partial_namespace(self):
        # Arrange
        linter = Linter(self.metadata, appendum=["stdlib.private"])

        # Act
        with open("test_appendum_partial.sh", "w") as f:
            f.write("stdlib.private.call 'arg'\n")
            f.write("stdlib.public.call 'arg'\n") # This should still error

        errors = linter.lint("test_appendum_partial.sh")
        if os.path.exists("test_appendum_partial.sh"):
            os.remove("test_appendum_partial.sh")

        # Assert
        # stdlib.private.call is ignored
        # stdlib.public.call should have an error (STD001)
        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0].CODE, "STD001")
        self.assertIn("stdlib.public", errors[0].message)

if __name__ == "__main__":
    unittest.main()
