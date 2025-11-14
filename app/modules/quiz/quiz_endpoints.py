from typing import List

from fastapi import APIRouter, Depends
from fastapi.security import HTTPBearer

from app.core.auth.protectors import AppTransport, secure_protector
from app.guards.access_control import access_required
from app.modules.quiz.dto.filter_dto import QuizFilterParams
from app.modules.quiz.dto.request_dto import QuizRequestDto
from app.modules.quiz.dto.response_dto import QuizResponseDto
from app.modules.quiz.loader import QuizLoader

quiz_router = APIRouter(
    prefix="/quizzes",
    tags=["quiz"],
    responses={
        200: {"description": "Success"},
        401: {"description": "Unauthorized"},
        404: {"description": "Not found"},
        500: {"description": "Internal server error"},
    },
)


@quiz_router.get(
    "/",
    summary="Retrieve all quizzes",
    description="Fetch a list of all quizzes.",
    dependencies=[Depends(HTTPBearer)],
    response_model=List[QuizResponseDto.GetQuizDTO] | QuizResponseDto.GetQuizDTO,
)
@access_required()
async def get_quizzes(
    filter_params: QuizFilterParams = Depends(),
    transport: AppTransport = Depends(secure_protector),
):
    return await QuizLoader.get(filter_params=filter_params, transport=transport)


@quiz_router.get(
    "/{quiz_id}/preview",
    summary="Preview quiz by ID",
    description="Get quiz details.",
    dependencies=[Depends(HTTPBearer)],
    response_model=List[QuizResponseDto.PreviewQuizDTO]
    | QuizResponseDto.PreviewQuizDTO,
)
@access_required()
async def preview_quiz(
    quiz_id: int,
    filter_params: QuizFilterParams = Depends(),
    transport: AppTransport = Depends(secure_protector),
):
    # TODO: cringe!!!
    return await QuizLoader.preview(
        model_id=quiz_id, transport=transport, filter_params=filter_params
    )


@quiz_router.post(
    "/",
    summary="Create new quiz",
    description="Create a new quiz.",
    dependencies=[Depends(HTTPBearer)],
    response_model=QuizResponseDto.CreateQuizDTO,
)
@access_required()
async def create_quiz(
    in_dto: QuizRequestDto.CreateQuiz,
    transport: AppTransport = Depends(secure_protector),
):
    return await QuizLoader.create(in_dto=in_dto, transport=transport)


@quiz_router.put(
    "/{quiz_id}",
    summary="Update quiz",
    description="Update an existing quiz entry.",
    dependencies=[Depends(HTTPBearer)],
    response_model=QuizResponseDto,
)
@access_required()
async def update_quiz(
    quiz_id: int,
    in_dto: QuizRequestDto.UpdateQuiz,
    transport: AppTransport = Depends(secure_protector),
):
    return await QuizLoader.update(model_id=quiz_id, in_dto=in_dto, transport=transport)


@quiz_router.delete(
    "/{quiz_id}",
    summary="Delete quiz",
    description="Remove a quiz.",
    dependencies=[Depends(HTTPBearer)],
)
@access_required()
async def delete_quiz(
    quiz_id: int, transport: AppTransport = Depends(secure_protector)
):
    return await QuizLoader.delete(model_id=quiz_id, transport=transport)
