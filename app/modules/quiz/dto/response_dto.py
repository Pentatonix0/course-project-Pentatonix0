from pydantic import ConfigDict, Field

from app.core.base_dto import BaseDto
from app.modules.user.dto.response_dto import UserResponseDto


class QuizResponseDto(BaseDto):
    class CreateQuizDTO(BaseDto):
        author_id: int = Field(gt=0)
        name: str = Field(min_length=1, max_length=50)
        description: str = Field(min_length=1, max_length=500)

    class PreviewQuizDTO(BaseDto):
        model_id: int = Field()
        name: str = Field(min_length=1, max_length=50)
        description: str = Field(min_length=1, max_length=500)

    class GetQuizDTO(PreviewQuizDTO):
        author: UserResponseDto.GetUserDTO = Field()

        model_config = ConfigDict(from_attributes=True)
