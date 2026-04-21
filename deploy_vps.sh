#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(dirname "$(readlink -f "$0")")"
ENV_FILE="$ROOT_DIR/.env"
CERT_LINK_DIR="$ROOT_DIR/docker/nginx/certs"
COMPOSE_ARGS=(-f docker-compose.yml -f docker-compose.production.yml)

require_command() {
    if ! command -v "$1" >/dev/null 2>&1; then
        printf 'Missing required command: %s\n' "$1" >&2
        exit 1
    fi
}

validate_domain() {
    local domain="$1"

    if [[ ! "$domain" =~ ^[A-Za-z0-9.-]+$ ]]; then
        return 1
    fi

    if [[ "$domain" == .* || "$domain" == *. || "$domain" == -* || "$domain" == *- ]]; then
        return 1
    fi

    if [[ "$domain" == *..* || "$domain" != *.* ]]; then
        return 1
    fi

    return 0
}

get_env_value() {
    local key="$1"

    if [ ! -f "$ENV_FILE" ]; then
        return 1
    fi

    grep -E "^${key}=" "$ENV_FILE" | tail -n 1 | cut -d '=' -f 2-
}

upsert_env() {
    local key="$1"
    local value="$2"

    if [ -f "$ENV_FILE" ] && grep -q -E "^${key}=" "$ENV_FILE"; then
        perl -0pi -e "s/^${key}=.*\$/""${key}=${value}""/m" "$ENV_FILE"
    else
        printf '%s=%s\n' "$key" "$value" >> "$ENV_FILE"
    fi
}

ensure_env_file() {
    if [ -f "$ENV_FILE" ]; then
        return
    fi

    cp "$ROOT_DIR/.env.example" "$ENV_FILE"
}

detect_cert_file() {
    local cert_dir="$1"
    local path

    for path in \
        "$cert_dir/fullchain.pem" \
        "$cert_dir/cert.pem" \
        "$cert_dir/certificate.crt" \
        "$cert_dir/tls.crt"
    do
        if [ -f "$path" ]; then
            printf '%s\n' "$path"
            return 0
        fi
    done

    return 1
}

detect_key_file() {
    local cert_dir="$1"
    local path

    for path in \
        "$cert_dir/privkey.pem" \
        "$cert_dir/key.pem" \
        "$cert_dir/private.key" \
        "$cert_dir/tls.key"
    do
        if [ -f "$path" ]; then
            printf '%s\n' "$path"
            return 0
        fi
    done

    return 1
}

main() {
    local default_domain cert_root cert_dir app_domain cert_file key_file

    require_command docker
    require_command perl

    ensure_env_file

    default_domain="$(get_env_value APP_DOMAIN || true)"
    cert_root="${CERT_ROOT:-/root/cert}"

    if [ -n "$default_domain" ]; then
        read -r -p "Domain for deploy [$default_domain]: " app_domain
        app_domain="${app_domain:-$default_domain}"
    else
        read -r -p 'Domain for deploy: ' app_domain
    fi

    if [ -z "$app_domain" ]; then
        printf 'Domain is required.\n' >&2
        exit 1
    fi

    if ! validate_domain "$app_domain"; then
        printf 'Invalid domain: %s\n' "$app_domain" >&2
        exit 1
    fi

    cert_dir="$cert_root/$app_domain"

    if [ ! -d "$cert_dir" ]; then
        printf 'Certificate directory not found: %s\n' "$cert_dir" >&2
        exit 1
    fi

    cert_file="$(detect_cert_file "$cert_dir" || true)"
    key_file="$(detect_key_file "$cert_dir" || true)"

    if [ -z "$cert_file" ] || [ -z "$key_file" ]; then
        printf 'Could not detect certificate pair in %s\n' "$cert_dir" >&2
        printf 'Expected one of: fullchain.pem/cert.pem/certificate.crt/tls.crt and privkey.pem/key.pem/private.key/tls.key\n' >&2
        exit 1
    fi

    mkdir -p "$CERT_LINK_DIR"
    ln -sfn "$cert_file" "$CERT_LINK_DIR/fullchain.pem"
    ln -sfn "$key_file" "$CERT_LINK_DIR/privkey.pem"

    upsert_env APP_DOMAIN "$app_domain"
    upsert_env FLASK_ENV production
    upsert_env TRUST_PROXY_COUNT 1
    upsert_env PREFERRED_URL_SCHEME https
    upsert_env SESSION_COOKIE_SECURE true
    upsert_env REMEMBER_COOKIE_SECURE true

    if ! grep -q -E '^NGINX_HTTP_PORT=' "$ENV_FILE"; then
        upsert_env NGINX_HTTP_PORT 80
    fi

    if ! grep -q -E '^NGINX_HTTPS_PORT=' "$ENV_FILE"; then
        upsert_env NGINX_HTTPS_PORT 443
    fi

    docker compose "${COMPOSE_ARGS[@]}" up -d --build
    docker compose "${COMPOSE_ARGS[@]}" ps

    printf 'HTTPS deploy prepared for https://%s\n' "$app_domain"
}

main "$@"
