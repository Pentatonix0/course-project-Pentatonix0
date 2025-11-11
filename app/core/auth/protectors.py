import json
from typing import Any, Dict

from fastapi import Depends, HTTPException, Request
from fastapi.security import HTTPBearer
from loguru import logger
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth.auth_dependencies import get_user
from app.data_base.data_base import get_db_session

security = HTTPBearer()


class AppTransport(BaseModel):
    method: str | None = Field(default=None)
    body: Dict[str, Any] | None = Field(default=None)
    request: Request | None = Field(default=None)
    db_session: AsyncSession | None = Field(default=None)
    user_id: int | None = Field(default=None)
    model_config = {"arbitrary_types_allowed": True}


async def protector(
    request: Request, db_session: AsyncSession = Depends(get_db_session)
) -> AppTransport:
    body = None
    try:
        content_type = request.headers.get("Content-Type", "")
        if "multipart/form-data" in content_type:
            # Для multipart/form-data читаем данные формы
            form_data = await request.form()
            body = {key: value for key, value in form_data.items()}
            # Если есть request_dto, пытаемся распарсить как JSON
            if "request_dto" in body:
                try:
                    # Safer JSON parsing: avoid implicit float -> binary float
                    body["request_dto"] = json.loads(
                        body["request_dto"], parse_float=str
                    )
                except json.JSONDecodeError:
                    logger.warning("request_dto is not a valid JSON, keeping as string")
        elif "application/json" in content_type:
            # Для JSON читаем тело как JSON
            body = await request.json()
    except json.JSONDecodeError:
        # Если тело пустое или невалидное, то оставляем body как None
        body = None
    except Exception as e:
        logger.error(f"Error reading request body: {e}")
        raise HTTPException(status_code=400, detail="Invalid request body")

    return AppTransport(
        method=request.method, body=body, db_session=db_session, request=request
    )


async def secure_protector(
    request: Request,
    db_session: AsyncSession = Depends(get_db_session),
    user_id=Depends(get_user),
):
    transport = await protector(request, db_session=db_session)
    transport.user_id = user_id
    return transport
