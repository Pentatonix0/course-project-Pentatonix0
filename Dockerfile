# syntax=docker/dockerfile:1.7

ARG PYTHON_VERSION=3.11.9
ARG PIP_VERSION=24.0
ARG SETUPTOOLS_VERSION=78.1.1
FROM python:${PYTHON_VERSION}-slim-bookworm AS base
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1
WORKDIR /app
RUN apt-get update \
    && apt-get upgrade -y --no-install-recommends \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

FROM base AS deps
ARG PIP_VERSION
ARG SETUPTOOLS_VERSION
ENV VIRTUAL_ENV=/opt/venv \
    PATH="/opt/venv/bin:${PATH}"
RUN python -m venv "${VIRTUAL_ENV}"
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade "pip==${PIP_VERSION}" "setuptools==${SETUPTOOLS_VERSION}" \
    && pip install --no-cache-dir -r requirements.txt

FROM deps AS tester
COPY requirements-dev.txt .
RUN pip install --no-cache-dir -r requirements-dev.txt
COPY . .
RUN pytest -q

FROM base AS runtime
ARG APP_USER=app
ARG APP_UID=10001
ARG APP_GID=10001
RUN groupadd --system --gid "${APP_GID}" "${APP_USER}" \
    && useradd --system --no-create-home --uid "${APP_UID}" --gid "${APP_GID}" "${APP_USER}"
ENV PATH="/opt/venv/bin:${PATH}"
WORKDIR /app
COPY --from=deps --chown=${APP_USER}:${APP_USER} /opt/venv /opt/venv
COPY --chown=${APP_USER}:${APP_USER} app ./app
COPY --chown=${APP_USER}:${APP_USER} applied_files ./applied_files
COPY --chown=${APP_USER}:${APP_USER} main.py ./main.py
RUN mkdir -p applied_files/logs \
    && chown -R "${APP_USER}:${APP_USER}" applied_files
EXPOSE 8021
HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 CMD ["python", "-c", "import sys, urllib.request; urllib.request.urlopen('http://127.0.0.1:8021/health', timeout=2).read()"]
USER ${APP_USER}
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8021"]
