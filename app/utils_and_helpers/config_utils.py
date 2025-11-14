import json
import os
from pathlib import Path

from loguru import logger

from app.core.core_dto import CoreDto
from app.core.errors import QuestBuilderError
from app.utils_and_helpers.core_helper import resource_path


def load_config(conf_path: Path) -> CoreDto | None:
    try:
        with open(conf_path, "r") as _json_file:
            conf = CoreDto(**json.loads(_json_file.read()))
            return conf
    except Exception as e:
        logger.error(e)
        raise QuestBuilderError(
            status_code=500, message=f"Failed in load config. Exeption = {e}"
        )


def set_config(config_dir: str = None) -> CoreDto:
    """Просто для удобства добавил сюда функцию подгрузки конфига приложения"""

    if config_dir is None:
        config_dir = resource_path("applied_files/config")
    conf_dir = Path(config_dir)
    conf_path = conf_dir.joinpath(Path("config.json"))
    if conf_path.exists():
        conf = load_config(conf_path)
    else:
        conf = CoreDto()
        conf_dir.mkdir(
            exist_ok=True, parents=True
        )  # Добавил parents=True для создания всей структуры директорий
        with open(conf_path, "w") as f:
            conf_for_write = conf.model_dump_json(indent=4)
            logger.debug(conf_for_write)
            f.write(conf_for_write)

    db_host = os.getenv("DB_HOST")
    server_host = os.getenv("SERVER_HOST")
    if db_host:
        logger.info(f"DB_HOST from env ={db_host}")
        conf.database_config.host = db_host
    if server_host:
        logger.info(f"SERVER_HOST from env ={server_host}")
        conf.server_config.host = server_host
    return conf


app_config = set_config(config_dir=None)
