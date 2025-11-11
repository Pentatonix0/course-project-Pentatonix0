# ADR-001 — Auth Tokens & Password Hashing

**Status:** Accepted
**Date:** 2025-11-02

## Context

Сервис использует регистрацию/логин и выдает JWT для доступа к защищённым эндпоинтам. Хранение паролей и выпуск токенов — критичные операции в нашей модели угроз.

Связи:

-   NFR: NFR-SEC-01 (хэширование), NFR-SEC-02 (TTL/алгоритм), NFR-SEC-06 (секреты/ротация)
-   Threat Model: F1 (register), F2/F9 (login/JWT)
-   Risks: R2 (пароли), R3 (TTL/утечка JWT)

## Decision

1. **Хэширование паролей**

-   Используем `bcrypt` (или `argon2id`) через `passlib.CryptContext`.
-   Вызовы — в `app/core/auth/auth_core.py`: `hash_password()` и `verify_password()`.

2. **JWT**

-   Алгоритм: **HS256**.
-   **Access TTL**: ~5 минут.
-   **Refresh TTL**: ~45 минут.
-   Обрабатываем `exp/iat/nbf`.
-   Секрет берём из ENV (`SECRET_KEY`)

## Consequences

-   Пароли не обратимы; стойкость к офлайн-атакам повышена.
-   Предсказуемая и измеримая политика жизни токенов.
-   Требования к конфигурации окружения: секреты — только в ENV, не в репозитории.

## Links

-   **Code:** `app/core/auth/auth_core.py`, эндпоинты `app/modules/auth/auth_endpoints.py`
-   **NFR:** NFR-SEC-01, NFR-SEC-02, NFR-SEC-06
-   **Threat Model:** F1, F2, F9
-   **Risks:** R2, R3

## Verification

-   unit: проверка bcrypt-хэша и верификации пароля
-   integration: регистрация/логин → валидные токены; заголовок JWT `alg=HS256`; `exp` в допустимом окне
