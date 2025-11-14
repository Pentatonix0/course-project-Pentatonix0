from abc import ABCMeta

from fastapi import HTTPException
from loguru import logger
from pydantic import BaseModel
from sqlalchemy import select

from app.core.auth.protectors import AppTransport
from app.core.base_filter_dto import BaseFilterParams
from app.data_base.app_declarative_base import Base


class BaseModelLoader(ABCMeta):
    db_model: type[Base] = None

    @classmethod
    async def get(cls, filter_params: BaseFilterParams, transport: AppTransport):
        filter_params_dict = filter_params.model_dump(exclude_defaults=True)
        query = select(cls.db_model).filter_by(**filter_params_dict)

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
    async def create(cls, in_dto: BaseModel, transport: AppTransport):
        logger.debug("BaseModelLoader.create")

        model = cls.db_model(**in_dto.model_dump(exclude_unset=True, exclude_none=True))
        transport.db_session.add(model)
        await transport.db_session.commit()
        await transport.db_session.refresh(model)

        return model

    @classmethod
    async def update(cls, model_id: int, in_dto: BaseModel, transport: AppTransport):
        logger.debug("BaseModelLoader.update")

        query = select(cls.db_model).filter_by(model_id=model_id)
        model = (await transport.db_session.execute(query)).scalar()

        if not model:
            raise HTTPException(
                status_code=404,
                detail=f"Model = {cls.db_model.__name__} with id={model_id} not found",
            )

        update_data = in_dto.model_dump(exclude_unset=True, exclude_none=True)
        for key, value in update_data.items():
            setattr(model, key, value)

        transport.db_session.add(model)
        await transport.db_session.commit()
        await transport.db_session.refresh(model)

        return model

    @classmethod
    async def delete(cls, model_id: int, transport: AppTransport):
        logger.debug("BaseModelLoader.delete")

        query = select(cls.db_model).filter_by(model_id=model_id)
        model = (await transport.db_session.execute(query)).scalar()

        if not model:
            raise HTTPException(
                status_code=404,
                detail=f"Model = {cls.db_model.__name__} with id={model_id} not found",
            )

        await transport.db_session.delete(model)
        await transport.db_session.commit()

        return {
            "detail": f"Model {cls.db_model.__name__} with id={model_id} deleted successfully"
        }
