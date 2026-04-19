FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends curl \
    && groupadd --system app \
    && useradd --system --gid app --create-home --home-dir /home/app app \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN chmod +x /app/docker/entrypoint.sh \
    && chown -R app:app /app

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
    CMD sh -c 'curl --fail --silent "http://127.0.0.1:${PORT:-8000}/healthz" >/dev/null || exit 1'

USER app

ENTRYPOINT ["/app/docker/entrypoint.sh"]
