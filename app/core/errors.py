import uuid
from typing import Any, Dict, List, Optional

from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import ValidationError


class QuestBuilderError(Exception):
    message: str
    status_code: int

    def __init__(self, message: str, status_code: int = 422):
        self.message = message
        self.status_code = status_code


def _correlation_id(request: Request) -> str:
    try:
        cid = getattr(request.state, "correlation_id", None)
        if not cid:
            cid = str(uuid.uuid4())
            request.state.correlation_id = cid
        return cid
    except Exception:
        return str(uuid.uuid4())


def _problem(
    *,
    status: int,
    title: str,
    detail: Optional[str] = None,
    type_: str = "about:blank",
    instance: Optional[str] = None,
    correlation_id: Optional[str] = None,
    errors: Optional[Dict[str, List[str]]] = None,
) -> Dict[str, Any]:
    problem: Dict[str, Any] = {
        "type": type_,
        "title": title,
        "status": status,
    }
    if detail:
        problem["detail"] = detail
    if instance:
        problem["instance"] = instance
    if correlation_id:
        problem["correlation_id"] = correlation_id
    if errors:
        problem["errors"] = errors
    return problem


async def quest_builder_exception_handler(request: Request, exc: QuestBuilderError):
    cid = _correlation_id(request)
    problem = _problem(
        status=exc.status_code,
        title="Application error",
        detail=exc.message,
        correlation_id=cid,
    )
    return JSONResponse(status_code=exc.status_code, content=problem)


async def http_exception_handler(request: Request, exc: HTTPException):
    cid = _correlation_id(request)
    # Do not leak internal details
    title = "HTTP error"
    detail = (
        None
        if exc.status_code >= 500
        else (exc.detail if isinstance(exc.detail, str) else None)
    )
    problem = _problem(
        status=exc.status_code, title=title, detail=detail, correlation_id=cid
    )
    return JSONResponse(status_code=exc.status_code, content=problem)


async def validation_exception_handler(request: Request, exc: ValidationError):
    cid = _correlation_id(request)
    field_errors: Dict[str, List[str]] = {}
    for err in exc.errors():
        loc = ".".join([str(p) for p in err.get("loc", [])]) or "_root_"
        field_errors.setdefault(loc, []).append(err.get("msg", "invalid"))
    problem = _problem(
        status=422, title="Validation error", correlation_id=cid, errors=field_errors
    )
    return JSONResponse(status_code=422, content=problem)


async def unhandled_exception_handler(request: Request, exc: Exception):
    cid = _correlation_id(request)
    # Mask internal details for clients
    problem = _problem(status=500, title="Internal Server Error", correlation_id=cid)
    return JSONResponse(status_code=500, content=problem)
