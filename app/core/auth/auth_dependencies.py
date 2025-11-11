from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError

from app.core.auth.auth_core import AuthCore

security = HTTPBearer()


async def get_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    try:
        data = await AuthCore.decode_token(token)
        user_id = int(data["sub"])
        return user_id
    except JWTError:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token",
        )
