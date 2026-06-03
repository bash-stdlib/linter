"""Base class for linter CLI commands."""

class Command:
    def execute(self, args):
        raise NotImplementedError
