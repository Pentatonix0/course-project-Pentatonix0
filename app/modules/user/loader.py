from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import selectinload

from app.core.auth.auth_core import AuthCore
from app.core.auth.protectors import AppTransport
from app.core.base_loader import BaseModelLoader
from app.modules.user.dto.filter_dto import UserFilterDto
from app.modules.user.dto.request_dto import UserRequestDto
from app.modules.user.user_data_base_model import User


class UserLoader(BaseModelLoader):
    db_model = User

    @classmethod
    async def get(cls, filter_params: UserFilterDto, transport: AppTransport):
        filter_params_dict = filter_params.model_dump(exclude_defaults=True)
        query = (
            select(cls.db_model)
            .options(
                selectinload(User.role),
            )
            .filter_by(**filter_params_dict)
        )

        if filter_params.limit:
            query = query.limit(filter_params.limit)
        if filter_params.offset:
            query = query.offset(filter_params.offset)
        if filter_params.order_by:
            query = query.order_by(filter_params.order_by)

        if not (model := (await transport.db_session.execute(query)).scalars().all()):
            raise HTTPException(
                status_code=404, detail=f"Model = {cls.db_model.__name__} not found"
            )
        return model

    @classmethod
    async def create(cls, in_dto: UserRequestDto.CreateUser, transport: AppTransport):

        in_dto.password = await AuthCore.hash_password(in_dto.password)
        try:
            return await super().create(in_dto=in_dto, transport=transport)
        except IntegrityError:
            raise HTTPException(
                status_code=400,
                detail="Нельзя создать несколько пользователей с одним именем или почтой",
            )

    @classmethod
    async def delete(cls, model_id: int, transport: AppTransport):
        query = (
            select(User).options(selectinload(User.role)).filter_by(model_id=model_id)
        )
        result = await transport.db_session.execute(query)
        user: User = result.scalar()
        if not user:
            raise HTTPException(
                status_code=404,
                detail=f"Model = {cls.db_model.__name__} with id={model_id} not found",
            )
        return await super().delete(model_id=model_id, transport=transport)

    @classmethod
    async def initialize_root_user(
        cls, transport: AppTransport, in_dto: UserRequestDto.CreateUser
    ):
        query = select(User).filter_by(username=in_dto.username)
        result = await transport.db_session.execute(query)
        existing_user: User = result.scalar_one_or_none()
        hashed_password = await AuthCore.hash_password(in_dto.password)
        if not existing_user:
            user = User(
                username=in_dto.username,
                email=in_dto.email,
                password=hashed_password,
                role_id=in_dto.role_id,
            )
            transport.db_session.add(user)
            try:
                await transport.db_session.commit()
            except IntegrityError:
                await transport.db_session.rollback()
