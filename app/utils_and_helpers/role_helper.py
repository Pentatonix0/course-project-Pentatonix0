from app.core.auth.protectors import AppTransport
from app.data_base.data_base import get_db_session
from app.modules.role.loader import RoleLoader


class RoleHelper:
    @classmethod
    async def initialize_roles(cls):
        async for db_session in get_db_session():
            transport = AppTransport(db_session=db_session)
            await RoleLoader.initialize_roles(transport=transport)
