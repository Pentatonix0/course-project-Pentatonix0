from fastapi import APIRouter, Depends

from app.core.auth.protectors import AppTransport, protector
from app.modules.auth.dto.request_dto import AuthRequestDto
from app.modules.auth.dto.response_dto import AuthResponseDto
from app.modules.auth.loader import AuthLoader

auth_router = APIRouter(
    prefix="/auth",
    tags=["auth"],
    responses={
        200: {"description": "Success"},
        401: {"description": "Unauthorized"},
        404: {"description": "Not found"},
        500: {"description": "Internal server error"},
    },
)


@auth_router.post(
    "/register",
    summary="Register",
    description="Registers a new user with username, email and password.",
    response_model=AuthResponseDto,
)
async def register(
    in_dto: AuthRequestDto.Register, transport: AppTransport = Depends(protector)
):
    return await AuthLoader.register(in_dto=in_dto, transport=transport)


@auth_router.post(
    "/login",
    summary="Login",
    description="Authenticates a user using login and password.",
    response_model=AuthResponseDto,
)
async def login(
    in_dto: AuthRequestDto.Login, transport: AppTransport = Depends(protector)
):
    return await AuthLoader.login(in_dto=in_dto, transport=transport)


@auth_router.post(
    "/refresh",
    summary="Refresh",
    description="Generates new tokens using a refresh token.",
    response_model=AuthResponseDto,
)
async def refresh(
    in_dto: AuthRequestDto.Refresh, transport: AppTransport = Depends(protector)
):
    return await AuthLoader.refresh(in_dto=in_dto, transport=transport)
