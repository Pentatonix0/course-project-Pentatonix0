import uuid
from typing import Callable

from fastapi import Request


class CorrelationIdMiddleware:
    def __init__(self, app: Callable):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope.get("type") != "http":
            await self.app(scope, receive, send)
            return

        async def send_wrapper(message):
            if message.get("type") == "http.response.start":
                headers = message.setdefault("headers", [])
                # Ensure header is set
                cid = scope.setdefault("state", {}).get("correlation_id")
                if not cid:
                    cid = str(uuid.uuid4())
                    scope["state"]["correlation_id"] = cid
                headers.append((b"x-request-id", cid.encode("utf-8")))
            await send(message)

        try:
            request = Request(scope, receive=receive)
            if not getattr(request.state, "correlation_id", None):
                request.state.correlation_id = str(uuid.uuid4())
        except Exception:
            pass

        await self.app(scope, receive, send_wrapper)
