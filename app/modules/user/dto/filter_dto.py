from pydantic import Field

from app.core.base_filter_dto import BaseFilterParams


class UserFilterDto(BaseFilterParams):
    role_id: int | None = Field(None, description="ID роли")
