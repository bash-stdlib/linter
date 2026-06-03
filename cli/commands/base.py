"""Base class for linter CLI commands."""


class Command:
    COMMAND_NAME = None

    def execute(self, args):
        raise NotImplementedError
