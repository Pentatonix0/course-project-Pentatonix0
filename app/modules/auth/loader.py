from collections import defaultdict, deque
from datetime import UTC, datetime, timedelta
from typing import DefaultDict, Deque, Dict

from fastapi import HTTPException
from jose import ExpiredSignatureError
from loguru import logger
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.core.auth.auth_core import AuthCore
from app.core.auth.protectors import AppTransport
from app.core.base_loader import BaseModelLoader
from app.modules.auth.dto.request_dto import AuthRequestDto
from app.modules.auth.dto.response_dto import AuthResponseDto
from app.modules.user.user_data_base_model import User


class AuthLoader(BaseModelLoader):

    # NFR-SEC-04: Rate limit ≤5 req/min/IP
    _RATE_WINDOW_SECONDS = 60
    _RATE_MAX_PER_WINDOW = 5
    _ip_requests: DefaultDict[str, Deque[datetime]] = defaultdict(deque)

    # NFR-SEC-04: Account lockout 15m after 10 errors
    _LOCKOUT_MAX_FAILURES = 10
    _LOCKOUT_DURATION = timedelta(minutes=15)
    _failed_attempts: DefaultDict[str, Deque[datetime]] = defaultdict(deque)
    _lockout_until: Dict[str, datetime] = {}

    @classmethod
    def _rate_limit_check(cls, ip: str) -> None:
        now = datetime.now(UTC)
        dq = cls._ip_requests[ip]
        # purge old
        while dq and (now - dq[0]).total_seconds() > cls._RATE_WINDOW_SECONDS:
            dq.popleft()
        if len(dq) >= cls._RATE_MAX_PER_WINDOW:
            raise HTTPException(status_code=429, detail="Too Many Requests")
        dq.append(now)

    @classmethod
    def _is_locked(cls, username: str) -> bool:
        until = cls._lockout_until.get(username)
        return bool(until and until > datetime.now(UTC))

    @classmethod
    def _register_failure_and_maybe_lock(cls, username: str) -> None:
        now = datetime.now(UTC)
        dq = cls._failed_attempts[username]
        # purge old (older than lockout window)
        while dq and (now - dq[0]) > cls._LOCKOUT_DURATION:
            dq.popleft()
        dq.append(now)
        if len(dq) >= cls._LOCKOUT_MAX_FAILURES:
            cls._lockout_until[username] = now + cls._LOCKOUT_DURATION
            logger.warning("account_lockout")

    @classmethod
    async def register(cls, in_dto: AuthRequestDto.Register, transport: AppTransport):
        """Регистрация нового пользователя"""
        logger.info("AuthLoader register")

        username = in_dto.username
        email = in_dto.email
        password = in_dto.password

        # Проверяем, нет ли пользователя с таким username или email
        query = select(User).filter((User.username == username) | (User.email == email))
        result = await transport.db_session.execute(query)
        existing_user = result.scalar()
        if existing_user:
            raise HTTPException(
                status_code=400,
                detail="User with this username or email already exists",
            )

        hashed_password = await AuthCore.hash_password(password)

        new_user = User(username=username, email=email, password=hashed_password)
        try:
            transport.db_session.add(new_user)
            await transport.db_session.commit()
            await transport.db_session.refresh(new_user)

            token_data = {"sub": str(new_user.model_id)}
            access_token = await AuthCore.create_access_token(token_data)
            refresh_token = await AuthCore.create_refresh_token(token_data)

            return AuthResponseDto(
                access_token=access_token, refresh_token=refresh_token
            )
        except IntegrityError:
            logger.error("IntegrityError during register")
            await transport.db_session.rollback()
            raise HTTPException(status_code=400, detail="Could not register user")

    @classmethod
    async def login(cls, in_dto: AuthRequestDto.Login, transport: AppTransport):
        logger.info("AuthLoader login")

        username = in_dto.username
        password = in_dto.password
        # NFR-SEC-04: rate limit per IP
        client_ip = "unknown"
        try:
            if transport.request and transport.request.client:
                client_ip = transport.request.client.host or "unknown"
        except Exception:
            client_ip = "unknown"
        cls._rate_limit_check(client_ip)

        # NFR-SEC-04: lockout check
        if cls._is_locked(username):
            logger.warning("account_lockout")
            # unified response, no PII
            raise HTTPException(status_code=401, detail="Invalid credentials")

        query = select(User).filter_by(username=username)
        result = await transport.db_session.execute(query)
        user: User = result.scalar()

        if not user:
            # count as failure towards lockout, but don't reveal existence
            cls._register_failure_and_maybe_lock(username)
            raise HTTPException(status_code=401, detail="Invalid credentials")

        if not await AuthCore.verify_password(password, user.password):
            cls._register_failure_and_maybe_lock(username)
            raise HTTPException(status_code=401, detail="Invalid credentials")

        token_data = {"sub": str(user.model_id)}

        access_token = await AuthCore.create_access_token(token_data)
        refresh_token = await AuthCore.create_refresh_token(token_data)

        return AuthResponseDto(access_token=access_token, refresh_token=refresh_token)

    @classmethod
    async def refresh(cls, in_dto: AuthRequestDto.Login, transport: AppTransport):
        logger.info("AuthLoader refresh")

        refresh_token = in_dto.refresh_token
        try:
            data = await AuthCore.decode_token(refresh_token)
            if not data:
                raise HTTPException(status_code=401, detail="Invalid refresh_token")
            user_id = int(data["sub"])
            if not user_id:
                raise HTTPException(status_code=401, detail="Invalid refresh_token")
            query = select(User).filter_by(model_id=user_id)
            result = await transport.db_session.execute(query)
            user: User = result.scalar()
            if not user:
                raise HTTPException(status_code=401, detail="Invalid refresh_token")
            token_data = {"sub": str(user.model_id)}
            access_token = await AuthCore.create_access_token(token_data)
            refresh_token = await AuthCore.create_refresh_token(token_data)
            return AuthResponseDto(
                access_token=access_token, refresh_token=refresh_token
            )
        except ExpiredSignatureError as er:
            logger.error(f"AuthLoader refresh expired: {er}")
            raise HTTPException(
                status_code=403, detail="AuthLoader refresh_token expired"
            )
