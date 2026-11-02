from schedule_manager.user.model import User
from schedule_manager.user.schemas import UserAdd


class UserSchemaTranslator:
    @staticmethod
    def to_model(schema: UserAdd) -> User:
        return User(name=schema.name)
