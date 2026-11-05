from schedule_manager.unit.model import Unit
from schedule_manager.unit.schemas import UnitAdd


class UnitSchemaTranslator:
    @staticmethod
    def to_model(schema: UnitAdd) -> Unit:
        return Unit(name=schema.name, business_id=schema.business_id)
