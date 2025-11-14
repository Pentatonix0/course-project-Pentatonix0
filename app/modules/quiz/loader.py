from fastapi.exceptions import HTTPException
from loguru import logger
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.core.auth.protectors import AppTransport
from app.core.base_loader import BaseModelLoader
from app.modules.quiz.dto.filter_dto import QuizFilterParams
from app.modules.quiz.dto.request_dto import QuizRequestDto
from app.modules.quiz.quiz_data_base_model import Quiz
from app.modules.user.user_data_base_model import User


class QuizLoader(BaseModelLoader):
    db_model = Quiz

    @classmethod
    async def get(cls, filter_params: QuizFilterParams, transport: AppTransport):
        """Получение списка квизов с фильтрацией"""
        logger.info("QuizLoader.get called")
        filter_params_dict = filter_params.model_dump(exclude_defaults=True)
        query = (
            select(Quiz)
            .options(selectinload(Quiz.author))
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
                status_code=404, detail=f"Model = {Quiz.__name__} not found"
            )
        return model

    @classmethod
    async def preview(
        cls, model_id: int, filter_params: QuizFilterParams, transport: AppTransport
    ):
        """Получение списка квизов с фильтрацией"""
        logger.info("QuizLoader.get called")
        # TODO: cringe!!!
        filter_params.model_id = model_id
        return await super().get(filter_params=filter_params, transport=transport)

    @classmethod
    async def create(cls, in_dto: QuizRequestDto.CreateQuiz, transport: AppTransport):
        """Создание нового квиза"""
        logger.info("QuizLoader.create called")

        # Проверка, что автор существует
        query = select(User).filter_by(model_id=in_dto.author_id)
        result = await transport.db_session.execute(query)
        author = result.scalar()

        if not author:
            raise HTTPException(
                status_code=404, detail=f"User with id={in_dto.author_id} not found"
            )

        return await super().create(in_dto=in_dto, transport=transport)

    @classmethod
    async def update(
        cls, model_id: int, in_dto: QuizRequestDto.UpdateQuiz, transport: AppTransport
    ):
        """Обновление существующего квиза"""
        logger.info(f"QuizLoader.update called for quiz_id={model_id}")

        return await super().update(
            model_id=model_id, in_dto=in_dto, transport=transport
        )

    @classmethod
    async def delete(cls, model_id: int, transport: AppTransport):
        """Удаление квиза"""
        logger.info(f"QuizLoader.delete called for quiz_id={model_id}")

        query = select(Quiz).filter_by(model_id=model_id)
        result = await transport.db_session.execute(query)
        quiz = result.scalar()

        if not quiz:
            raise HTTPException(
                status_code=404, detail=f"Quiz with id={model_id} not found"
            )

        # если у квиза есть связанные вопросы, можно добавить каскадное удаление здесь
        return await super().delete(model_id=model_id, transport=transport)
