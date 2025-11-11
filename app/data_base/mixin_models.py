from app.utils_and_helpers.config_utils import app_config


class SchemaMixin:
    """Миксины для указания пользровательской схемы"""

    __schema__ = app_config.database_config.schema_name
    __table_args__ = {"schema": __schema__}
