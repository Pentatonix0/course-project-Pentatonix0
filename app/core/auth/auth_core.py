import asyncio
import os
from datetime import UTC, datetime, timedelta
from typing import Optional

from dotenv import load_dotenv
from jose import JWTError, jwt
from passlib.context import CryptContext

load_dotenv()

pwd_context = CryptContext(
    schemes=["argon2"],
    deprecated="auto",
    # NFR-SEC-01: Argon2id with fixed parameters
    argon2__type="ID",
    argon2__memory_cost=65536,  # ~64MB
    argon2__time_cost=3,
    argon2__parallelism=1,
)


class AuthCore:
    ALGORITHM = "HS256"
    SECRET_KEY = os.getenv("SECRET_KEY", "default-insecure-key")
    ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 15))
    REFRESH_TOKEN_EXPIRE_MINUTES = int(os.getenv("REFRESH_TOKEN_EXPIRE_MINUTES", 10080))

    @classmethod
    async def hash_password(cls, password: str) -> str:
        """Асинхронное хэширование пароля через Argon2"""
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, pwd_context.hash, password)

    @classmethod
    async def verify_password(cls, plain_password: str, hashed_password: str) -> bool:
        """Проверка пароля"""
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(
            None, pwd_context.verify, plain_password, hashed_password
        )

    @classmethod
    async def create_access_token(
        cls, data: dict, expire_delta: Optional[timedelta] = None
    ) -> str:
        """Создание Access JWT токена"""
        to_encode = data.copy()
        expire = datetime.now(UTC) + (
            expire_delta or timedelta(minutes=cls.ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        to_encode.update({"exp": expire, "type": "access"})
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(
            None, jwt.encode, to_encode, cls.SECRET_KEY, cls.ALGORITHM
        )

    @classmethod
    async def create_refresh_token(cls, data: dict) -> str:
        """Создание Refresh JWT токена"""
        to_encode = data.copy()
        expire = datetime.now(UTC) + timedelta(minutes=cls.REFRESH_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire, "type": "refresh"})
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(
            None, jwt.encode, to_encode, cls.SECRET_KEY, cls.ALGORITHM
        )

    @classmethod
    async def decode_token(cls, token: str) -> Optional[dict]:
        """Декодирование и проверка токена"""
        loop = asyncio.get_running_loop()
        try:
            return await loop.run_in_executor(
                None, jwt.decode, token, cls.SECRET_KEY, [cls.ALGORITHM]
            )
        except JWTError:
            return None
