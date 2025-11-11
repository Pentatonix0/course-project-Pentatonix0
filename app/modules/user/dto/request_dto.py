from pydantic import Field

from app.core.base_dto import BaseDto


class UserRequestDto(BaseDto):
    class CreateUser(BaseDto):
        username: str = Field(min_length=1, max_length=50)
        email: str = Field(min_length=1, max_length=120)
        password: str = Field(min_length=1, max_length=50)
