Контекст

Нужно было добавить проверки IaC и контейнера (P12): Hadolint по Dockerfile, Checkov по IaC, Trivy по образу, с отчётами в `EVIDENCE/P12/` и отдельным workflow.

Что сделано

- Создан workflow `.github/workflows/ci-p12-iac-container.yml` (push/pull_request/dispatch, `concurrency` на `p12-iac-container-${{ github.ref }}`, `permissions: contents, packages`).
- В пайплайне собирается runtime-образ `quiz-builder:p12`, далее: Hadolint (docker образ hadolint, конфиг `security/hadolint.yaml`) выводит JSON в `EVIDENCE/P12/hadolint_report.json`; Checkov (bridgecrew/checkov, конфиг `security/checkov.yaml`) сканирует `iac/` и пишет `checkov_report.json`; Trivy (aquasec/trivy:latest, конфиг `security/trivy.yaml`) сканирует образ и пишет `trivy_report.json`.
- Добавлены конфиги линтеров/сканеров: `security/hadolint.yaml` (ослаблены некоторые предупреждения, failure-threshold warning), `security/checkov.yaml` (soft_fail, kubernetes), `security/trivy.yaml` (HIGH/CRITICAL, vuln os+library).
- IaC манифесты вынесены в `iac/deployment.yaml` и `iac/service.yaml` (Deployment + Service, non-root user 10001, запрет privilege escalation, ресурсы, порт 8021).
- Каталог `EVIDENCE/P12/` с README зафиксирован в репо; workflow загружает артефакт `p12-iac-container`.

Как проверял

- Workflow гонялся в Actions: сборка образа проходит; Trivy отчёт формируется; Hadolint/Checkov шаги теперь пишут отчёты в `EVIDENCE/P12` (исправлены пути и создание каталога). Следующий запуск должен дать полный комплект `hadolint_report.json`, `checkov_report.json`, `trivy_report.json` и артефакт.
- Локально сверял Dockerfile/порт/healthcheck (8021, `/health`) и структуру `iac/`, чтобы сканеры находили файлы и сервис стартовал в CI.
