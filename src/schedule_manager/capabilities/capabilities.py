from enum import Enum, auto
from dataclasses import dataclass
from schedule_manager.capabilities.errors import InvalidCapabilitiesCombinationError

class AutoLowerEnum(str, Enum):
    @staticmethod
    def _generate_next_value_(name, start, count, last_values):
        return name.lower()

class Resource(AutoLowerEnum):
    BUSINESS = auto()
    UNIT = auto()
    WORKSTATION = auto()


    BUSINESS_HOLIDAYS = auto()
    UNIT_HOLIDAYS = auto()
    WORKSTATION_HOLIDAYS = auto()

    MEMBERS = auto()


class Action(AutoLowerEnum):
    READ = auto()
    MANAGE = auto()
    INVITE = auto()


class Scope(str, Enum):
    BUSINESS = "business"
    UNIT = "unit"
    WORKSTATION = "workstation"


SCOPE_BY_RESOURCE = {
    Resource.BUSINESS: Scope.BUSINESS,
    Resource.UNIT: Scope.UNIT,
    Resource.WORKSTATION: Scope.WORKSTATION,

    Resource.BUSINESS_HOLIDAYS: Scope.BUSINESS,
    Resource.UNIT_HOLIDAYS: Scope.UNIT,
    Resource.WORKSTATION_HOLIDAYS: Scope.WORKSTATION,

    Resource.MEMBERS: Scope.BUSINESS,
}


COLUMN_BY_SCOPE = {
    Scope.BUSINESS: "business_id",
    Scope.UNIT: "unit_id",
    Scope.WORKSTATION: "workstation_id",
}

def choose_scope(resource:Resource) -> Scope:
    return SCOPE_BY_RESOURCE[resource]

@dataclass(frozen=True)
class Capability:
    resource: Resource
    action: Action

    def __post_init__(self):
        if self.action == Action.INVITE and self.resource != Resource.MEMBERS:
            raise InvalidCapabilitiesCombinationError("Only members support invite")

    @property
    def name(self) -> str:
        return f"{self.resource.value}_{self.action.value}"

    @property
    def scope(self) -> Scope:
        return choose_scope(self.resource)

    @property
    def column_name(self) -> str:
        return COLUMN_BY_SCOPE[self.scope]

def capability_from_name(name: str) -> Capability:
    resource_name, action_name = name.rsplit("_", 1)

    try:
        resource = Resource(resource_name)
        action = Action(action_name)
    except ValueError:
        raise ValueError(f"Invalid capability name: {name!r}") from None

    return Capability(resource, action)