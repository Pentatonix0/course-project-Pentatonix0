from typing import List

from fastapi import APIRouter, Depends
from fastapi.security import HTTPBearer

from app.core.auth.protectors import AppTransport, secure_protector
from app.guards.access_control import access_required
from app.modules.user.dto.filter_dto import UserFilterDto
from app.modules.user.dto.request_dto import UserRequestDto
from app.modules.user.dto.response_dto import UserResponseDto
from app.modules.user.loader import UserLoader

user_router = APIRouter(
    prefix="/user",
    tags=["user"],
    responses={
        200: {"description": "Success"},
        401: {"description": "Unauthorized"},
        404: {"description": "Not found"},
        500: {"description": "Internal server error"},
    },
)


@user_router.get(
    "/",
    summary="Retrieve all users",
    description="Returns users based on the specified filtering parameters.",
    dependencies=[Depends(HTTPBearer)],
    response_model=List[UserResponseDto.GetUserDTO],
)
@access_required()
async def get_users(
    transport: AppTransport = Depends(secure_protector),
    filter_params: UserFilterDto = Depends(),
):
    return await UserLoader.get(filter_params=filter_params, transport=transport)


@user_router.post(
    "/",
    summary="Add user for software",
    description="Creates a new user record in the database.",
    dependencies=[Depends(HTTPBearer)],
    response_model=UserResponseDto.CreateUserDTO,
)
@access_required()
async def add_user(
    in_dto: UserRequestDto.CreateUser,
    transport: AppTransport = Depends(secure_protector),
):
    return await UserLoader.create(in_dto=in_dto, transport=transport)


@user_router.delete(
    "/{model_id}",
    summary="Delete user",
    description="Deletes a user record from the database by its unique ID.",
    dependencies=[Depends(HTTPBearer)],
)
@access_required()
async def delete_user(
    model_id: int, transport: AppTransport = Depends(secure_protector)
):
    return await UserLoader.delete(model_id=model_id, transport=transport)
