from functools import wraps
from typing import Callable

from fastapi import HTTPException
from fastapi.security import HTTPBearer
from loguru import logger
from sqlalchemy import select

from app.modules.user.user_data_base_model import User

security = HTTPBearer()


def access_required():
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            logger.debug(f"Permission decorator for {func.__name__}")

            transport = kwargs.get("transport")
            user_id = transport.user_id
            if not user_id:
                raise HTTPException(status_code=401, detail="Authentication required")

            query = select(User).filter_by(model_id=user_id)
            result = await transport.db_session.execute(query)
            user: User = result.scalar()
            if not user:
                raise HTTPException(
                    status_code=404, detail=f"User with id={user_id} not found"
                )

            return await func(*args, **kwargs)

        return wrapper

    return decorator
