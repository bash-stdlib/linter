"""Error for unclosed function scopes."""

from errors.base import LinterErrorBase


class STD009(LinterErrorBase):
    """Reported when a function definition is missing a closing brace."""

    CODE = "STD009"
    TITLE = "Unclosed function scope"
    DESCRIPTION = (
        "A function definition was started but no matching closing brace was found."
    )

    def format_message(self) -> str:
        return (
            f"Unclosed function scope detected for '{self.match}' "
            f"starting at line {self.line}."
        )
