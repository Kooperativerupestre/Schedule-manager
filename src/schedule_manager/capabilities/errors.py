class DuplicateCapabilityError(Exception):
    pass

class NullCapabilityError(Exception):
    pass

class TargetNotFoundError(Exception):
    pass
class CapabilityNameError(Exception):
    pass
class CapabilityNotFoundError(Exception):
    pass

class ForbiddenError(Exception):
    pass
class InvalidCapabilitiesCombinationError(Exception):
    pass