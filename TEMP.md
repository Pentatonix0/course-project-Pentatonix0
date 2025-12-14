Контекст

Нужно было добавить DAST-проверку (OWASP ZAP baseline) для курсового сервиса в CI: поднять приложение на раннере, прогнать ZAP по локальному URL и сложить отчёты в `EVIDENCE/P11/` + загрузить артефакт.

Что сделано

- Создан отдельный workflow `.github/workflows/ci-p11-dast.yml`, триггеры на push/pull_request/workflow_dispatch, `concurrency` на `dast-zap-${{ github.ref }}` и разрешения `contents: read`, `packages: read` (для pull образов из GHCR).
- Джоб `zap-baseline` собирает runtime-образ, поднимает стек через `docker compose up -d api`, ждёт health чек `./scripts/wait-for-health.sh api 40 3` (сервис слушает `http://localhost:8021/health`).
- Запуск ZAP: тянем образ `ghcr.io/zaproxy/zaproxy:stable` (авторизация через `GITHUB_TOKEN`), при недоступности GHCR fallback на `docker.io/owasp/zap2docker-stable:latest`. Запускаем `zap-baseline.py -t http://localhost:8021 -J /zap/wrk/zap_baseline.json -r /zap/wrk/zap_baseline.html -I`, рабочая директория и volume мапятся на `EVIDENCE/P11`.
- После прогона выкладываем артефакт `p11-dast-zap` с `zap_baseline.html/json` и пишем краткую сводку в `GITHUB_STEP_SUMMARY`. Каталог `EVIDENCE/P11/` зафиксирован в репо (README).

Как проверял

- Workflow гонялся в GitHub Actions на ветке `p11-dast-zap`; стек поднимается, ZAP образ теперь успешно тянется (через GHCR либо fallback). Следующий прогон должен сформировать `EVIDENCE/P11/zap_baseline.*` и артефакт `p11-dast-zap`.
- Healthcheck сервиса проверяется скриптом в пайплайне; локально перед пушем собирал и запускал `docker compose up -d --build api`, чтобы убедиться, что `/health` отвечает 200 на 8021.
