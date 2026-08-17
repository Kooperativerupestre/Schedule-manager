from schedule_manager.config import settings
from datetime import datetime, timezone, timedelta
from uuid import UUID
import jwt


def generate_token(person_id: UUID) -> str:
    payload = {
        "sub": str(person_id),
        "exp": datetime.now(timezone.utc) + timedelta(hours=6),
    }
    return jwt.encode(payload, settings.jwt_secret_key, settings.jwt_algorithm)
