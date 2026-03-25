# Stage 1: dependency build
FROM python:3.12-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    pkg-config \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Stage 2: runtime
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

ARG USER_UID=1000
ARG USER_GID=1000
ARG APP_PORT=8000

# Persist build args as runtime env vars (build.sh needs them)
ENV USER_UID=${USER_UID} \
    USER_GID=${USER_GID} \
    APP_PORT=${APP_PORT}

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    gosu \
    && rm -rf /var/lib/apt/lists/*

RUN groupadd -r -g "${USER_GID}" appuser \
    && useradd -r -u "${USER_UID}" -g appuser appuser

COPY --from=builder /usr/local/lib/python3.12/site-packages/ /usr/local/lib/python3.12/site-packages/
COPY --from=builder /usr/local/bin/ /usr/local/bin/

COPY --chown=${USER_UID}:${USER_GID} . /app
RUN chmod 755 /app/build.sh && sed -i 's/\r$//' /app/build.sh

EXPOSE ${APP_PORT}

ENTRYPOINT ["/app/build.sh"]
CMD ["sh", "-c", "daphne -b 0.0.0.0 -p ${APP_PORT:-8000} config.asgi:application"]
