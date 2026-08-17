from fastapi import Cookie, HTTPException
from uuid import UUID
from schedule_manager.config import settings
import jwt


async def get_current_person_id(access_token: str = Cookie(None)) -> UUID:
    if access_token is None:
        raise HTTPException(status_code=401, detail="Not authenticated")

    try:
        payload = jwt.decode(
            access_token, settings.jwt_secret_key, algorithms=["HS256"]
        )
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invaid token")
    return UUID(payload["sub"])
