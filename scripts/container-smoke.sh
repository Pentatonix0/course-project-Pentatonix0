#!/usr/bin/env bash
set -euo pipefail

IMAGE_NAME="${IMAGE_NAME:-quiz-builder:local}"
SERVICE_NAME="${SERVICE_NAME:-api}"
COMPOSE_CMD="${COMPOSE_COMMAND:-docker compose}"

cleanup() {
    ${COMPOSE_CMD} down --remove-orphans >/dev/null 2>&1 || true
}
trap cleanup EXIT

${COMPOSE_CMD} up -d --build "${SERVICE_NAME}"
./scripts/wait-for-health.sh "${SERVICE_NAME}"

uid="$(${COMPOSE_CMD} exec -T "${SERVICE_NAME}" id -u)"
if [[ "${uid}" -eq 0 ]]; then
    echo "Container is running as root, expected non-root user" >&2
    exit 10
fi

echo "Container smoke-test succeeded (UID=${uid})."
