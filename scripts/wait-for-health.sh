#!/usr/bin/env bash
set -euo pipefail

SERVICE_NAME="${1:-api}"
MAX_ATTEMPTS="${2:-30}"
SLEEP_SECONDS="${3:-2}"
COMPOSE_CMD="${COMPOSE_COMMAND:-docker compose}"

container_id="$(${COMPOSE_CMD} ps -q "${SERVICE_NAME}")"
if [[ -z "${container_id}" ]]; then
    echo "Service ${SERVICE_NAME} is not running" >&2
    exit 1
fi

for attempt in $(seq 1 "${MAX_ATTEMPTS}"); do
    status="$(docker inspect -f '{{.State.Health.Status}}' "${container_id}" 2>/dev/null || true)"
    if [[ "${status}" == "healthy" ]]; then
        echo "Container ${container_id} is healthy"
        exit 0
    fi
    if [[ "${status}" == "unhealthy" ]]; then
        echo "Container ${container_id} is unhealthy" >&2
        docker logs "${container_id}" || true
        exit 2
    fi
    sleep "${SLEEP_SECONDS}"
done

echo "Timed out waiting for ${SERVICE_NAME} to become healthy" >&2
${COMPOSE_CMD} ps "${SERVICE_NAME}" || true
exit 3
