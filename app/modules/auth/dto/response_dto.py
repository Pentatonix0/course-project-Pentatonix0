from pydantic import Field

from app.core.base_dto import BaseDto


class AuthResponseDto(BaseDto):
    access_token: str = Field()
    refresh_token: str = Field()
