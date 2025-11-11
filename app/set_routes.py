from typing import List

from fastapi import APIRouter
from loguru import logger


async def set_routes(all_routes: List[APIRouter], app):
    logger.info("Set routes")
    for _router in all_routes:
        logger.info(f"Set route {_router.tags}")
        logger.info(f"Set route {_router.routes}")
        app.include_router(_router, prefix="/api/v1")
