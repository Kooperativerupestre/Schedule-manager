from fastapi import Response, Cookie
from uuid import UUID
from schedule_manager.auth.jwt import generate_token

def set_cookie(response:Response, id:UUID) -> None:
    response.set_cookie(
        key="access_token",
        value=generate_token(id),
        httponly=True,
        secure=False,
        samesite="lax"
    )
def clear_cookie(response:Response) -> None:
    response.delete_cookie(
        key="access_token",
        httponly=True,
        secure=True,
        samesite="lax"
    )
