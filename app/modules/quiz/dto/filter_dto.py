from pydantic import Field

from app.core.base_filter_dto import BaseFilterParams


class QuizFilterParams(BaseFilterParams):
    name: str | None = Field(None, description="Название квеста")
