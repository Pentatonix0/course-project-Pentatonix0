from enum import Enum


class UserRole(str, Enum):
    ROOT = "root"
    ADMIN = "admin"
    USER = "user"

    async def level(self) -> int:
        return {UserRole.ROOT: 993, UserRole.ADMIN: 992, UserRole.USER: 991}[self]
