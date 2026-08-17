from enum import Enum, auto


class UpdateOutputs(Enum):
    ZERO_CHANGES = auto()
    NOT_EXECUTED = auto()
    OK = auto()
