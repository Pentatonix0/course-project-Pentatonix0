from typing import Dict, Optional

import httpx


def get_async_client(
    *,
    timeout_connect: float = 2.0,
    timeout_read: float = 5.0,
    timeout_write: float = 5.0,
    timeout_pool: float = 5.0,
    max_connections: int = 100,
    max_keepalive: int = 20,
    headers: Optional[Dict[str, str]] = None,
) -> httpx.AsyncClient:
    timeout = httpx.Timeout(
        connect=timeout_connect,
        read=timeout_read,
        write=timeout_write,
        pool=timeout_pool,
    )
    limits = httpx.Limits(
        max_connections=max_connections, max_keepalive_connections=max_keepalive
    )
    default_headers = {"User-Agent": "quiz-builder-httpx/1.0"}
    if headers:
        default_headers.update(headers)
    return httpx.AsyncClient(timeout=timeout, limits=limits, headers=default_headers)


async def get_with_retries(
    client: httpx.AsyncClient,
    url: str,
    *,
    retries: int = 2,
    backoff: float = 0.3,
    headers: Optional[Dict[str, str]] = None,
) -> httpx.Response:
    last_exc: Optional[Exception] = None
    for attempt in range(retries + 1):
        try:
            return await client.get(url, headers=headers)
        except (httpx.ReadTimeout, httpx.ConnectError, httpx.RemoteProtocolError) as e:
            last_exc = e
            if attempt == retries:
                break
            # naive backoff
            import asyncio

            await asyncio.sleep(backoff * (attempt + 1))
    assert last_exc is not None
    raise last_exc
