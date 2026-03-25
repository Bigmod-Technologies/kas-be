#!/bin/bash
set -e

# Fix mounted volume permissions (for root-owned host mounts)
if [ "$(id -u)" = "0" ] && command -v gosu >/dev/null 2>&1; then
    chown -R "${USER_UID:-1000}:${USER_GID:-1000}" /app/static
fi

echo "Starting Django application..."

echo "Waiting for PostgreSQL..."
python - <<'PY'
import os
import time
import psycopg2

host = os.environ.get("DB_HOST")
port = int(os.environ.get("DB_PORT", "5432"))
user = os.environ.get("DB_USER")
password = os.environ.get("DB_PASSWORD")
database = os.environ.get("DB_NAME")

for attempt in range(30):
    try:
        conn = psycopg2.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=database,
        )
        conn.close()
        print("PostgreSQL is ready.")
        break
    except psycopg2.OperationalError:
        print(f"PostgreSQL not ready, attempt {attempt + 1}/30")
        time.sleep(2)
else:
    print("PostgreSQL never became ready")
    raise SystemExit(1)
PY

if [ -z "${SKIP_MIGRATIONS:-}" ]; then
    echo "Running migrations..."
    python manage.py migrate --noinput
    echo "Collecting static files..."
    python manage.py collectstatic --noinput
else
    echo "Skipping migrations and collectstatic (SKIP_MIGRATIONS is set)."
fi

# Execute app command as unprivileged user in production
if command -v gosu >/dev/null 2>&1 && id appuser >/dev/null 2>&1; then
    exec gosu appuser "$@"
else
    exec "$@"
fi
