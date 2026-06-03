from typing import NamedTuple

class LinterError(NamedTuple):
    file: str
    line: int
    column: int
    message: str
    match: str

    def to_dict(self):
        return self._asdict()
