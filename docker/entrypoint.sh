#!/bin/sh
set -eu

log() {
    printf '%s\n' "$1"
}

fail() {
    log "[entrypoint] ERROR $1"
    exit 1
}

runtime_env="${APP_ENV:-${FLASK_ENV:-production}}"
port="${PORT:-8000}"
bind_host="${GUNICORN_HOST:-0.0.0.0}"
gunicorn_bind="${GUNICORN_BIND:-${bind_host}:${port}}"
gunicorn_workers="${WEB_CONCURRENCY:-${GUNICORN_WORKERS:-2}}"
gunicorn_timeout="${GUNICORN_TIMEOUT:-120}"
database_url="${DATABASE_URL:-${SQLALCHEMY_DATABASE_URI:-}}"

if [ -z "${database_url}" ]; then
    fail "DATABASE_URL or SQLALCHEMY_DATABASE_URI must be set before container startup."
fi

if [ "$runtime_env" = "production" ] && [ -z "${FLASK_SECRET_KEY:-}" ]; then
    fail "FLASK_SECRET_KEY must be set when FLASK_ENV=production."
fi

log "[entrypoint] waiting for database availability"

python3 - <<'PY'
import os
import time
from urllib.parse import urlparse

import psycopg2


database_url = os.environ.get("DATABASE_URL") or os.environ["SQLALCHEMY_DATABASE_URI"]
parsed = urlparse(database_url)


def _sanitize(value: str) -> str:
    host = parsed.hostname or "unknown-host"
    database = (parsed.path or "").lstrip("/") or "unknown-db"
    return f"{host}/{database}"

for attempt in range(30):
    try:
        connection = psycopg2.connect(database_url)
        connection.close()
        print(f"[entrypoint] database ready target={_sanitize(database_url)} attempt={attempt + 1}")
        break
    except psycopg2.OperationalError as exc:
        print(
            f"[entrypoint] database wait target={_sanitize(database_url)} "
            f"attempt={attempt + 1} error={exc.__class__.__name__}: {exc}"
        )
        time.sleep(2)
else:
    raise SystemExit("database did not become ready in time")
PY

log "[entrypoint] running database migrations"
if flask --app wsgi.py db upgrade; then
    log "[entrypoint] database migrations finished"
else
    fail "database migrations failed"
fi

log "[entrypoint] starting gunicorn bind=${gunicorn_bind} workers=${gunicorn_workers} timeout=${gunicorn_timeout} env=${runtime_env}"
exec gunicorn \
    --bind "${gunicorn_bind}" \
    --workers "${gunicorn_workers}" \
    --timeout "${gunicorn_timeout}" \
    --worker-tmp-dir /dev/shm \
    --access-logfile - \
    --error-logfile - \
    wsgi:app
