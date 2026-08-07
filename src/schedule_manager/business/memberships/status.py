from enum import Enum, auto

class InviteStatus(Enum):
    @staticmethod
    def _generate_next_value_(name, start, count, last_values):
        return name.lower()
    ACCEPTED = auto()
    PENDING = auto()
    EXPIRED = auto()
    RECUSED = auto()

class MembershipStatus(Enum):
    @staticmethod
    def _generate_next_value_(name, start, count, last_values):
        return name.lower()
    ACTIVE = auto()
    ENDED = auto()
