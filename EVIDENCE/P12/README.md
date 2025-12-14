# P12 - IaC & Container Security evidence

Отчёты генерируются в CI workflow `ci-p12-iac-container.yml`:

- `hadolint_report.json` — результаты lint Dockerfile.
- `checkov_report.json` — результаты проверки IaC (`iac/`) через Checkov.
- `trivy_report.json` — отчёт по уязвимостям образа `quiz-builder:p12`.

После запуска workflow скачайте артефакт `p12-iac-container` или скопируйте файлы отсюда в PR.
