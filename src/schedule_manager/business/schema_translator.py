from schedule_manager.business.model import Business
from schedule_manager.business.schemas import BusinessAdd


class BusinessSchemaTranslator:
    @staticmethod
    def to_model(schema: BusinessAdd) -> Business:
        return Business(name=schema.name)
