import os
import sys
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from fastapi.security import HTTPBearer
from loguru import logger

from app.all_routes import all_routers
from app.core.core import core

# from app.utils_and_helpers.role_helper import RoleHelper
# from app.utils_and_helpers.user_helper import UserHelper
from app.core.errors import (
    QuestBuilderError,
    http_exception_handler,
    quest_builder_exception_handler,
    unhandled_exception_handler,
    validation_exception_handler,
)
from app.core.middlewares.correlation import CorrelationIdMiddleware
from app.data_base.data_base import Database
from app.set_routes import set_routes
from app.utils_and_helpers.config_utils import app_config

logger.add(
    app_config.logger_info.log_file,
    format="{time} {level} {message}",
    level=app_config.logger_info.level,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await core.init(app_config)
    await Database.initialize(app_config.database_config)
    await set_routes(all_routers, app)
    # await RoleHelper.initialize_roles()
    # await UserHelper.initialize_root_user()
    yield


app = FastAPI(lifespan=lifespan)

# Security schema
bearer_scheme = HTTPBearer()


# Кастомный OpenAPI
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="Quiz Builder API",
        version="1.0.0",
        description="API documentation with JWT authorization",
        routes=app.routes,
    )
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        }
    }
    for path in openapi_schema["paths"].values():
        for method in path.values():
            method["security"] = [{"BearerAuth": []}]
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi

# Добавляем CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(CorrelationIdMiddleware)

app.add_exception_handler(QuestBuilderError, quest_builder_exception_handler)
app.add_exception_handler(Exception, unhandled_exception_handler)
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)

this_file_path = sys.path.append(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)


@app.get("/")
async def root():
    return {"status": "Ok"}


@app.get("/health")
def health():
    return {"status": "ok"}


# # Example minimal entity (for tests/demo)
# _DB = {"items": []}


# @app.post("/items")
# def create_item(name: str):
#     if not name or len(name) > 100:
#         raise ApiError(
#             code="validation_error", message="name must be 1..100 chars", status=422
#         )
#     item = {"id": len(_DB["items"]) + 1, "name": name}
#     _DB["items"].append(item)
#     return item


# @app.get("/items/{item_id}")
# def get_item(item_id: int):
#     for it in _DB["items"]:
#         if it["id"] == item_id:
#             return it
#     raise ApiError(code="not_found", message="item not found", status=404)


if __name__ == "__main__":
    uvicorn.run(
        app,
        host=app_config.server_config.host,
        port=app_config.server_config.port,
        reload=app_config.server_config.reload,
    )
