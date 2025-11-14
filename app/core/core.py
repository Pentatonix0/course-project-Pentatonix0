class Core:
    """Класс для управления основными настройками приложения с использованием Singleton"""

    _instance = None
    _config = None
    _initialized = False

    def __new__(cls, config=None):
        if cls._instance is None:
            cls._instance = super(Core, cls).__new__(cls)
            if config is not None and cls._config is None:
                cls._config = config
            cls._initialized = True
        return cls._instance

    async def init(self, config):
        self._config = config


core = Core()
