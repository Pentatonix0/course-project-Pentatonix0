from app.core.auth.protectors import AppTransport
from app.core.roles import UserRole
from app.data_base.data_base import get_db_session
from app.modules.role.loader import RoleLoader
from app.modules.user.dto.request_dto import UserRequestDto
from app.modules.user.loader import UserLoader


class UserHelper:
    ROOT_USERNAME = "root"
    ROOT_PASSWORD = "123456789"
    ROOT_EMAIL = "mail@mail.ru"

    @classmethod
    async def initialize_root_user(cls):
        async for db_session in get_db_session():
            transport = AppTransport(db_session=db_session)
            root_role = await RoleLoader.get_role(UserRole.ROOT, transport=transport)
            in_dto = UserRequestDto.CreateUser(
                username=cls.ROOT_USERNAME,
                email=cls.ROOT_EMAIL,
                password=cls.ROOT_PASSWORD,
                role_id=root_role.model_id,
            )
            await UserLoader.initialize_root_user(transport, in_dto)
