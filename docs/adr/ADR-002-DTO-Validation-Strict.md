# ADR-002 — Strict DTO Validation (Pydantic v2)

**Status:** Accepted
**Date:** 2025-11-02

## Context

Нужно запретить «лишние» поля и гарантировать типобезопасность входного JSON на всех слоях (угрозы F5, риски R8).

Связи:

-   NFR: NFR-SEC-05 (валидация входных данных)
-   Threat Model: F5 (POST /quizzes + лишние поля)
-   Risks: R8 (целостность DTO)

## Decision

-   Вводим единый базовый класс DTO с конфигом **`extra="forbid"`** (Pydantic v2 — `ConfigDict`):
    файл `app/core/core_dto.py`.
-   Все схемы в `app/modules/**/dto/request_dto.py` наследуются от этого базового класса.

## Consequences

-   Любые неизвестные поля → **422**.
-   Схемы самодокументируются в OpenAPI, без «скрытых» расширений.

## Links

-   **Code:** `app/core/core_dto.py`, `app/modules/**/dto/request_dto.py`
-   **NFR:** NFR-SEC-05
-   **Threat Model:** F5
-   **Risks:** R8

## Verification

-   negative: `/auth/register` с лишним полем → **422**
-   (опционально) negative: любые CRUD-эндпоинты с «hack»-полем → **422**
