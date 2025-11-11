# ADR-003 — Error Handling as RFC 7807 (problem+json)

**Status:** Accepted
**Date:** 2025-11-02

## Context

Ошибки не должны раскрывать детали реализации (стектрейсы, пути, секреты). Клиентам нужен стабильный формат, удобный для машинной обработки.

Связи:

-   NFR: NFR-SEC-08 (ошибки без утечек), NFR-SEC-12 (не логировать токены/секреты)
-   Threat Model: F2/F3 (ошибки при login/me), F6 (тяжёлые GET)
-   Risks: R6 (утечки в ошибках/логах)

## Decision

-   Центральный error-мэппер в `app/core/errors.py`, возвращающий **RFC 7807** (`application/problem+json`) .

## Consequences

-   Единый безопасный формат ошибок; отсутствие PII/секретов в ответах.
-   Упрощённые e2e-проверки и наблюдаемость.

## Links

-   **Code:** `app/core/errors.py` (+ подключение в `main.py`)
-   **NFR:** NFR-SEC-08, NFR-SEC-12
-   **Threat Model:** F2, F3, F6
-   **Risks:** R6

## Verification

-   negative: 404/422/500 не содержат `Traceback` и секретов; контент-тайп problem+json
