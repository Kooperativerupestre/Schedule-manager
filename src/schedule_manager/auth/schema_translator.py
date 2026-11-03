from schedule_manager.auth.model import Authentication
from schedule_manager.auth.schemas import AuthenticationCreate


class AuthenticationSchemaTranslator:
    @staticmethod
    def to_model(
        schema: AuthenticationCreate,
        password_hash: str,
    ) -> Authentication:
        return Authentication(
            user_id=schema.user_id,
            email=str(schema.email),
            password_hash=password_hash,
        )
