import unittest
import os
from linter import Linter

class TestLinterAppendum(unittest.TestCase):
    def setUp(self):
        self.metadata = {
            "functions": {"stdlib.echo": {}},
            "namespaces": ["stdlib"]
        }

    def test_lint__appendum_function__returns_no_errors(self):
        linter = Linter(self.metadata, appendum=["stdlib.__message.get"])

        with open("test_appendum.sh", "w") as f:
            f.write("stdlib.__message.get 'hello'\n")

        errors = linter.lint("test_appendum.sh")
        if os.path.exists("test_appendum.sh"):
            os.remove("test_appendum.sh")

        self.assertEqual(len(errors), 0)

    def test_lint__appendum_namespace__returns_no_errors(self):
        linter = Linter(self.metadata, appendum=["my_ns"])

        with open("test_appendum_ns.sh", "w") as f:
            f.write("my_ns.foo 'bar'\n")

        errors = linter.lint("test_appendum_ns.sh")
        if os.path.exists("test_appendum_ns.sh"):
            os.remove("test_appendum_ns.sh")

        self.assertEqual(len(errors), 0)

    def test_lint__appendum_partial_namespace__returns_errors_only_for_non_appendum_calls(self):
        linter = Linter(self.metadata, appendum=["stdlib.private"])

        with open("test_appendum_partial.sh", "w") as f:
            f.write("stdlib.private.call 'arg'\n")
            f.write("stdlib.public.call 'arg'\n")

        errors = linter.lint("test_appendum_partial.sh")
        if os.path.exists("test_appendum_partial.sh"):
            os.remove("test_appendum_partial.sh")

        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0].CODE, "STD001")
        self.assertIn("stdlib.public", errors[0].message)

if __name__ == "__main__":
    unittest.main()
