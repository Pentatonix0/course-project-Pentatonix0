# Матрица трассировки NFR ↔ Stories / Tasks

## Идентификаторы историй / задач

| ID     | Название                               |
| ------ | -------------------------------------- |
| AUTH-1 | Регистрация / Логин (эндпоинты)        |
| AUTH-2 | JWT выпуск / проверка / ротация        |
| AUTH-3 | Лимитер логина                         |
| API-1  | CRUD Quizzes                           |
| API-2  | Валидация DTO (extra=forbid)           |
| API-3  | CORS конфигурация                      |
| CI-1   | Gitleaks в pre-commit / CI             |
| CI-2   | Пакетный аудит зависимостей            |
| OBS-1  | Аудит-логирование событий безопасности |
| OPS-1  | Регламент ротации секретов             |
| OPS-2  | Резервное копирование БД               |

---

## Матрица трассировки

| NFR ID     | Stories / Tasks | Приоритет |
| ---------- | --------------- | --------- |
| NFR-SEC-01 | AUTH-1, AUTH-2  | P1        |
| NFR-SEC-02 | AUTH-2, OPS-1   | P1        |
| NFR-SEC-03 | API-1, AUTH-2   | P1        |
| NFR-SEC-04 | AUTH-3          | P1        |
| NFR-SEC-05 | API-2, API-1    | P2        |
| NFR-SEC-06 | CI-1, OPS-1     | P1        |
| NFR-SEC-07 | CI-2            | P1        |
| NFR-SEC-08 | API-1           | P2        |
| NFR-SEC-09 | API-3           | P3        |
| NFR-SEC-10 | OBS-1           | P3        |
| NFR-SEC-11 | OPS-2           | P4        |
| NFR-SEC-12 | OBS-1, CI-1     | P2        |

---

## Рекомендации к бэклогу (Issues)

-   **AUTH-2:** Настроить JWT TTL (15m/7d), HS256, ротацию секрета, тесты на exp/alg
-   **AUTH-3:** Добавить rate-limiting (SlowAPI) для /auth/login
-   **API-2:** Все Pydantic DTO должны иметь `extra=forbid`; добавить негативные тесты
-   **CI-1:** Добавить gitleaks в CI и pre-commit, fail при любой утечке
-   **CI-2:** Добавить pip-audit/safety в CI, fail при High+ уязвимостях
-   **OBS-1:** Реализовать аудит-логи login/logout и ошибок доступа
-   **OPS-1:** Документировать процедуру ротации JWT-секрета ≤90d
-   **OPS-2:** Документировать ежедневные бэкапы БД, Retention 7d, тест восстановления
