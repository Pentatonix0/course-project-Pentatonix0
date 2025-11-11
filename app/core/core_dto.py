from pydantic import BaseModel, Field

from app.utils_and_helpers.core_helper import resource_path

# ==========================================================================


class LoggerDto(BaseModel):
    log_file: str = Field(
        default=resource_path("applied_files/logs/main.log"),
        description="Путь до файла логов",
    )
    level: str = Field(
        default="INFO",
        description="Уровень логирования (DEBUG, INFO, WARNING, ERROR, CRITICAL)",
    )

    rotation_trigger: str = Field(
        default="100 MB", description="Максимальный размер лога"
    )
    compression: str = Field(default="tar", description="Тип сжатия логов")
    retention: str = Field(
        default="7 day", description="Период хранения старых логов после сжатия"
    )


# ==========================================================================


class ServerDto(BaseModel):
    host: str = Field(default="0.0.0.0", description="IP-адрес сервера")
    port: int = Field(default=8021, description="Порт сервера")
    reload: bool = Field(
        default=True,
        description="Автоматический перезапуск сервера, при внесении изменений в код",
    )


# ==========================================================================


class DataBaseConfigDto(BaseModel):
    database_user: str = Field(
        default="postgres_user", description="Пользователь базы данных"
    )
    database_password: str = Field(
        default="password", description="Пароль пользователя базы данных"
    )
    data_base_name: str = Field(
        default="quest_builder_db", description="Наименование базы данных"
    )
    schema_name: str = Field(
        default="quest_builder_schema", description="Наименование схемы базы данных"
    )
    host: str = Field(default="localhost", description="IP-адрес базы данных")
    port: int = Field(default=5432, description="Порт базы данных")
    future: bool = Field(
        default=True,
        description="Флаг для на версиях 1.4 и 2.0 SQLAlchemy",
    )
    echo: bool = Field(default=True, description="Логирование событий БД")
    pool_size: int = Field(default=5, description="Максимальное количество соединений")
    max_overflow: int = Field(
        default=10, description="Максимальное количество соединений сверх лимита"
    )


# ==========================================================================


class CoreDto(BaseModel):
    logger_info: LoggerDto = Field(default=LoggerDto())
    database_config: DataBaseConfigDto = Field(default=DataBaseConfigDto())
    server_config: ServerDto = Field(default=ServerDto())


# ==========================================================================
