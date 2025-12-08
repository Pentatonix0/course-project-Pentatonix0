## Контекст

Собрал минимальный прод-образ FastAPI сервиса с базовым харднингом: multi-stage Dockerfile, non-root runtime, healthchecks и reproducible deps, плюс инфраструктура для локального запуска (compose + DB) и проверки в CI (Hadolint, Trivy, smoke‑тест). Также усилил конфиги: .env, .dockerignore, Makefile/scripts, обновил пайплайн и закрыл критичные CVE, задокументировав оставшиеся исключения.

## Что сделано

1. **Dockerfile и образ**
   - Полный multi-stage (base→deps→tester→runtime) на `python:3.11.9-slim-bookworm` с обновлением apt + pinned pip/setuptools (`Dockerfile`).
   - Deps строятся в venv, тесты гоняются на стадии `tester`, в runtime копируется только нужное, файлы принадлежат `app` (UID 10001) и `HEALTHCHECK` через Python.
   - ENV/ARG позволяют reproducible builds, лишние слои/кеши убраны.
2. **Compose и локальный запуск**
   - `docker-compose.yml` описывает API + Postgres 16.3 (healthcheck, volume, secret env, без проброса наружу).
   - API ждёт БД, имеет healthcheck на `/health`, порты/секреты читаются из `.env`.
   - `.env.example`, `.dockerignore`, `Makefile`, `scripts/wait-for-health.sh` и `scripts/container-smoke.sh` облегчают локальный запуск, проверку UID ≠ 0 и health.
3. **CI и сканеры**
   - Workflow разделён на build (lint/pytest/pre-commit) и container jobs (`.github/workflows/ci.yml`).
   - Container job: hadolint, docker build, compose up, ожидание health, проверка non-root, Trivy image scan с артефактом `trivy-report`.
   - `on: push + pull_request`, шаг upload всегда выполняется.
   - `.trivyignore` фиксирует CVE без доступных патчей (linux-pam/sqlite/zlib/ecdsa/starlette) с обоснованием.
4. **Зависимости и CVE**
   - Обновлены FastAPI/Starlette/Uvicorn, установлены setuptools==78.1.1, зафиксирован pip==24.0, исправлены версии в requirements*.
   - Dockerfile обновлён для установки безопасных версий ещё на базовой стадии.
   - Trivy теперь зелёный (Debian 12.12 без HIGH/CRITICAL, Python CVE покрыты или задокументированы).

## Как проверял

- Локально: `pytest -q tests/test_health.py`, `make hadolint`, `make smoke`.
- CI: GitHub Actions (ruff/black/isort/pytest, compose stack, Hadolint, Trivy scan с артефактом отчёта).
