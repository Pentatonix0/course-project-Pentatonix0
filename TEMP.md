Контекст

Нужно было собрать минимальный CI-конвейер для ветки p08-cicd-minimal, который на push и pull_request гарантированно гоняет линтеры, тесты и минимальные проверки контейнера с воспроизводимой установкой зависимостей.

Что сделано

- Workflow `.github/workflows/ci.yml` триггерится на push/pull_request, включает `permissions: contents: read` и `concurrency` c ключом `ci-${{ github.ref }}`, чтобы отменять параллельные прогоны.
- Джоб `build` готовит Python 3.11 через `actions/setup-python@v5` с кешом pip и ставит зависимости из `requirements*.txt`, после чего прогоняет Ruff/Black/isort, минимальные тесты `pytest -q tests/test_health.py` и `pre-commit run --all-files`.
- Джоб `container` переиспользует код, собирает runtime-образ (`docker build --target runtime`), поднимает сервис `api` через compose, ждёт healthcheck скриптом `scripts/wait-for-health.sh`, проверяет, что процесс не под root, и завершает docker-compose окружение даже при ошибках.
- Дополнительные проверки: Hadolint для Dockerfile, Trivy-скан образа с артефактом `trivy-report`, таким образом требование по отчётам закрыто.

Как проверял

- Workflow прогонялся в GitHub Actions на ветке `p08-cicd-minimal`: оба джоба прошли зелёным, в разделе Artifacts приложен `trivy-report`.
- Минимальный тест `pytest -q tests/test_health.py` запускал локально перед пушем, чтобы убедиться, что API стартует и health ручка отвечает.
- Перед пушем собирал контейнер и проверял compose `docker compose up -d --build api`, чтобы healthcheck в CI не падал.
