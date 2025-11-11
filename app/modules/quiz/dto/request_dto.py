from pydantic import Field

from app.core.base_dto import BaseDto


class QuizRequestDto(BaseDto):
    class CreateQuiz(BaseDto):
        author_id: int = Field(gt=0)
        name: str = Field(min_length=1, max_length=50)
        description: str = Field(min_length=1, max_length=500)

    class UpdateQuiz(BaseDto):
        name: str = Field(min_length=1, max_length=50)
        description: str = Field(min_length=1, max_length=500)
