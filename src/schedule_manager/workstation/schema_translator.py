from schedule_manager.workstation.model import Workstation
from schedule_manager.workstation.schemas import WorkstationAdd


class WorkstationSchemaTranslator:
    @staticmethod
    def to_model(workstation: WorkstationAdd) -> Workstation:
        return Workstation(
            name=workstation.name,
            unit_id=workstation.unit_id,
        )
