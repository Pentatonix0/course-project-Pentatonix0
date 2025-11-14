from pydantic import Field

from app.core.base_dto import BaseDto


class UserResponseDto(BaseDto):
    class CreateUserDTO(BaseDto):
        model_id: int = Field()
        username: str = Field()
        email: str = Field()

    class GetUserDTO(CreateUserDTO):
        pass
