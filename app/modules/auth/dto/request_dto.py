from pydantic import EmailStr, Field

from app.core.base_dto import BaseDto


class AuthRequestDto(BaseDto):
    class Login(BaseDto):
        username: str = Field(min_length=1, max_length=50)
        password: str = Field(min_length=1, max_length=50)

    class Register(Login):
        email: EmailStr

    class Refresh(BaseDto):
        refresh_token: str = Field()
