Контекст

Проработал NFR/STRIDE‑требования для аутентификации и API: строгая валидация DTO, унифицированные ошибки (RFC 7807) с correlation_id, защита от брутфорса на /auth/login, безопасные утилиты, а также базовое покрытие тестами основных и негативных сценариев.

Что сделано

- Хэширование и JWT:
  - Зафиксирован Argon2id с параметрами (m≈64MB, t=3, p=1) в `app/core/auth/auth_core.py`.
  - Дефолтные TTL по NFR: Access=15m, Refresh=7d в `app/core/auth/auth_core.py`.
- Login защита и ответы:
  - Rate‑limit 5 req/min на IP и блокировка учётки на 15 минут после 10 ошибок (лог‑событие `account_lockout`) в `app/modules/auth/loader.py`.
  - Унифицированные ответы при логине: всегда `401 Invalid credentials` без PII в `app/modules/auth/loader.py`.
- RFC 7807 и correlation_id:
  - Middleware с `X-Request-ID` (UUID) в `app/core/middlewares/correlation.py`.
  - Обработчики Problem+JSON для `HTTPException`, `ValidationError`, `Exception` в `app/core/errors.py`; подключение в `main.py`.
- Строгая валидация DTO:
  - Базовый `BaseDto` с `extra=forbid` в `app/core/base_dto.py` и применение в DTO: `app/modules/**/dto/*`.
  - Безопасный парсинг JSON: `parse_float=str` в `app/core/auth/protectors.py`.
- БД/SQL‑безопасность:
  - Валидация `schema_name` по `^[A-Za-z0-9_]+$` перед `CREATE SCHEMA` в `app/data_base/data_base.py`.
- Утилиты:
  - Безопасные файлы: UUID‑имена, canonical path, запрет симлинков, magic bytes в `app/utils_and_helpers/file_utils.py`.
  - Безопасный HTTP‑клиент (таймауты, пулы, ретраи) в `app/utils_and_helpers/http_client.py`.
- Тесты (покрытие позитивов и негативов):
  - `tests/test_auth.py` — базовые health, register/login, refresh.
  - `tests/test_user.py` — 403 без токена для GET/POST/DELETE.
  - `tests/test_quiz.py` — полный CRUD‑флоу с аутентификацией + негатив на несуществующего автора.
  - `tests/test_validation.py` — 422 с Problem+JSON и `correlation_id` на extra‑поле.
  - `tests/test_rate_limit.py` — 429 при частых логинах.
  - Единый `TestClient` на сессию в `tests/conftest.py` (устранение конфликтов event loop/БД на Windows).

Как проверял

- Локально запускал тесты: `pytest -q`.
- Ручная проверка ошибочных ответов (Problem+JSON) и заголовка `X-Request-ID` через curl.
- Проверил, что без `Authorization` защищённые ручки отдают 403 (поведение `HTTPBearer`), а при логине с неверными данными — унифицированный `401` без утечек.

