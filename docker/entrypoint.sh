#!/bin/sh
set -eu

echo "[entrypoint] waiting for database"

python3 - <<'PY'
import os
import time

import psycopg2


database_url = os.environ["DATABASE_URL"]

for attempt in range(30):
    try:
        connection = psycopg2.connect(database_url)
        connection.close()
        print(f"[entrypoint] database ready on attempt {attempt + 1}")
        break
    except psycopg2.OperationalError as exc:
        print(f"[entrypoint] database not ready: {exc}")
        time.sleep(2)
else:
    raise SystemExit("database did not become ready in time")
PY

echo "[entrypoint] running database migrations"
flask --app wsgi.py db upgrade

echo "[entrypoint] starting gunicorn"
exec gunicorn --bind 0.0.0.0:8000 wsgi:app
