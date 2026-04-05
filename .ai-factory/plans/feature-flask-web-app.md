# Implementation Plan: Flask Web App for SMM Assistant

Branch: feature/flask-web-app
Created: 2026-04-05

## Settings
- Testing: yes
- Logging: standard
- Docs: yes

## Summary

Current repository already contains reusable business logic for:
- post text generation (`generators/text_gen.py`)
- image generation (`generators/image_gen.py`)
- VK publishing (`social_publishers/vk_publisher.py`)
- platform stats collection (`social_stats/stats_collector.py`)

Main gaps and technical debt found during reconnaissance:
- missing real `config.py` despite imports from `config`
- demo-oriented root scripts (`test.py`, `test_env.py`, `run_tests.py`) mixed with application concerns
- mixed logging styles (`loguru`, `logging`, `print`) and `logging.basicConfig()` inside library classes
- weak error boundaries for web integration (`None` on failures, broad exceptions, direct stdout prints)
- no Flask app structure, auth, DB layer, or Docker/Postgres infrastructure

Implementation direction:
- keep the project as a single Flask web application for MVP, not as real microservices
- preserve existing generation/publishing/statistics logic where it is safe and valuable
- wrap legacy modules behind Flask service-layer adapters and normalize configuration/error handling
- introduce PostgreSQL + SQLAlchemy + Flask-Login + Flask-WTF + bcrypt-based password hashing

## Commit Plan
- **Commit 1** (after tasks 1-3): `feat: bootstrap flask app and database foundation`
- **Commit 2** (after tasks 4-6): `feat: add auth dashboard and vk settings flows`
- **Commit 3** (after tasks 7-9): `feat: add vk capability checks and content workflow integration`
- **Commit 4** (after tasks 10-12): `feat: add vk stats tests and application safeguards`
- **Commit 5** (after tasks 13-14): `chore: dockerize app and refresh deployment docs`

## Tasks

### Phase 1: Restructure Foundation

- [x] Task 1: Create Flask application skeleton using app factory pattern in `app/__init__.py`, `app/config.py`, `app/extensions.py`, `app/wsgi.py`, and package folders for `auth`, `main`, `settings`, `content`, and `stats` blueprints.
  Files: `app/__init__.py`, `app/config.py`, `app/extensions.py`, `app/wsgi.py`, `app/auth/__init__.py`, `app/main/__init__.py`, `app/settings/__init__.py`, `app/content/__init__.py`, `app/stats/__init__.py`, optional root `wsgi.py`.
  Logging requirements: log app startup configuration summary without secrets, DB URI host/database only, blueprint registration, and startup failures at INFO/ERROR; keep `LOG_LEVEL` environment-driven.

- [x] Task 2: Introduce database layer with PostgreSQL-first configuration using Flask-SQLAlchemy and migrations via Flask-Migrate, plus installable settings loading from env.
  Files: `requirements.txt`, `app/extensions.py`, `app/config.py`, `migrations/` (created by tool), `.env.example`.
  Logging requirements: log DB initialization attempts, migration/bootstrap execution, and configuration validation failures at INFO/ERROR without printing credentials.

- [x] Task 3: Define persistence models for users, VK settings, and generation history/publication results; add password hashing with bcrypt-compatible approach and user loader for sessions.
  Files: `app/models/__init__.py`, `app/models/user.py`, `app/models/vk_settings.py`, `app/models/generated_post.py` (or equivalent), `app/auth/login_manager.py` if needed.
  Logging requirements: log model-level lifecycle only at service boundaries, user creation/update events with IDs only, and validation failures at INFO/WARN; never log raw passwords, tokens, or full post content by default.

### Phase 2: Authentication and Core UI

- [x] Task 4: Implement registration, login, and logout flows with Flask-Login and Flask-WTF forms, including CSRF protection, flash messages, duplicate-user protection, and redirect behavior for unauthorized users.
  Files: `app/auth/routes.py`, `app/auth/forms.py`, `app/templates/auth/login.html`, `app/templates/auth/register.html`, `app/templates/base.html`.
  Depends on: 1, 2, 3.
  Logging requirements: log auth flow entry, successful login/logout, failed validation, duplicate email attempts, and auth errors with user email masked or partially redacted; use INFO/WARN/ERROR.

- [x] Task 5: Build dashboard and shared Bootstrap-based layout with navigation, flash message rendering, and authenticated page structure.
  Files: `app/main/routes.py`, `app/templates/base.html`, `app/templates/dashboard.html`, shared partials if needed.
  Depends on: 1, 4.
  Logging requirements: log dashboard access for authenticated user IDs, navigation/action entry points, and rendering failures at INFO/ERROR.

- [x] Task 6: Implement user settings page for VK credentials (`vk_api_key`, `vk_group_id`) with form validation, create-or-update persistence logic, safe UI messaging, and persisted connection metadata such as last validation status, last validation error code/message summary, and last successful validation timestamp.
  Files: `app/settings/routes.py`, `app/settings/forms.py`, `app/templates/settings.html`, `app/services/settings_service.py`.
  Depends on: 3, 4, 5.
  Logging requirements: log settings save attempts, validation failures, and successful updates by user ID only; never log raw VK token, only token presence/length metadata if needed.

### Phase 3: Service Integration and Business Flows

- [x] Task 7: Refactor legacy generation and VK integration modules into reusable service adapters with normalized exceptions, app-level logging, timeouts, fixed VK API version handling, and dependency injection-friendly constructors.
  Files: `generators/text_gen.py`, `generators/image_gen.py`, `social_publishers/vk_publisher.py`, `social_stats/stats_collector.py`, new `app/services/openai_service.py`, `app/services/vk_service.py`, optional shared error module.
  Depends on: 1, 2.
  Logging requirements: log external call start/finish, provider name, model/group IDs, chosen VK API version, retry/timeouts, and sanitized error context; remove direct `print()` and `logging.basicConfig()` usage from reusable modules.

- [x] Task 8: Implement VK capability validation service that verifies token shape, group access, publish prerequisites, and safe fallback behavior before auto-posting is attempted in UI flows.
  Files: `app/services/vk_capability_service.py`, `app/services/settings_service.py`, `social_publishers/vk_publisher.py`, `social_stats/stats_collector.py`, optional updates to `app/models/vk_settings.py`.
  Depends on: 6, 7.
  Logging requirements: log validation attempts by user ID and group ID, capability check outcomes, detected permission/access failures, and fallback decisions at INFO/WARN/ERROR; never log raw token values.

- [x] Task 9: Implement post generator page and use case flow: accept `tone`, `topic`, `generate image`, `auto post to VK`; generate text, optionally generate image, optionally publish to VK using saved user settings, persist result metadata/history, and always return generated content even if VK posting is unavailable or rejected.
  Files: `app/content/routes.py`, `app/content/forms.py`, `app/templates/content/generator.html`, `app/services/content_workflow.py`, `app/models/generated_post.py` or equivalent.
  Depends on: 3, 4, 6, 7, 8.
  Logging requirements: log workflow start/end, selected options, VK capability decisions, external integration calls, persisted result IDs, partial-success outcomes, and sanitized failures; do not log secrets and avoid logging full generated text above INFO.

- [x] Task 10: Implement VK stats page with minimum subscriber count using `groups.getById(fields=members_count)` first, plus fallback to `groups.getMembers` when needed; add only small extra metrics if they are safe and cheap.
  Files: `app/stats/routes.py`, `app/templates/stats/vk_stats.html`, `app/services/stats_service.py`, `social_stats/stats_collector.py` if extension is needed.
  Depends on: 4, 6, 7, 8.
  Logging requirements: log stats fetch request per user ID and group ID, selected VK method (`groups.getById` vs `groups.getMembers`), API version, upstream VK responses in summarized form, empty/misconfigured settings cases, and failures at INFO/WARN/ERROR.

### Phase 4: UX Safety, Scripts, and Cleanup

- [x] Task 11: Add application-level error handling, friendly failure pages, standardized flash messaging, and cleanup of legacy entrypoints so demo/test scripts are no longer confused with Flask runtime.
  Files: `app/errors.py` (or blueprint), `app/templates/errors/400.html`, `app/templates/errors/404.html`, `app/templates/errors/500.html`, root `test.py`, `test_env.py`, `run_tests.py`, optional `scripts/` directory.
  Depends on: 4, 5, 9, 10.
  Logging requirements: log uncaught exceptions with request path and user ID if present, validation errors, and script relocation/deprecation notes; never expose tracebacks in browser responses.

- [x] Task 12: Add automated tests for critical flows: config/app factory, auth, models, VK settings form flow, VK capability validation, content generation workflow with mocks, partial-success VK failures, and protected routes.
  Files: `tests/`, likely reorganized into `tests/unit/` and `tests/integration/`, shared fixtures in `tests/conftest.py`, updated `pytest.ini`.
  Depends on: 1 through 11.
  Logging requirements: test helpers should capture and assert structured failures where relevant; no secrets in fixtures; log only when diagnosing failed integration mocks.

### Phase 5: Deployment Readiness

- [x] Task 13: Containerize the application for VPS deployment with `Dockerfile`, `docker-compose.yml`, Postgres volume, env-driven config, app startup command, DB readiness check, migration bootstrap on container startup, and production-oriented defaults.
  Files: `Dockerfile`, `docker-compose.yml`, `.dockerignore`, optional `docker/entrypoint.sh`, `.env.example`.
  Depends on: 1, 2, 11.
  Logging requirements: log container startup phases, DB readiness wait status, migration execution, and app boot success/failure at INFO/ERROR; keep secrets out of startup output.

- [x] Task 14: Update project documentation for the new Flask/Postgres/Docker deployment model, including local run and VPS run via Docker Compose, required env vars, migration/bootstrap step, VK token capability caveats, and known operational caveats.
  Files: `README.md`, `docs/getting-started.md`, `docs/configuration.md`, `docs/architecture.md`, `docs/testing.md`, optional `docs/deployment.md`, `AGENTS.md`.
  Depends on: 13.
  Logging requirements: document runtime log expectations and where to inspect container/app logs during deployment troubleshooting.

## Notes and Risks

- The current repository has a broken or missing configuration module referenced by both code and tests. This must be corrected early because it affects nearly every legacy module.
- Existing OpenAI/VK/Telegram integrations are synchronous. For MVP they can stay synchronous, but long-running requests may block the Flask worker during generation or publishing.
- User-level storage of VK API credentials in PostgreSQL is required by the task. Implementation should avoid plaintext exposure in logs and UI; if time allows, assess whether at-rest encryption is warranted for VPS deployment.
- Current VK documentation adds a product risk: wall publishing and wall-photo upload require user access tokens with restricted rights (`wall`, `photos`). The plan therefore must treat VK auto-post as conditional capability rather than guaranteed success for every user.
- `groups.getById` response format changed in VK API v5.139, so the implementation should pin VK API version and isolate response parsing behind one adapter.
- Telegram-specific logic is outside the requested web MVP and should not drive new UI scope, but its existing modules should not be broken by the refactor.
- The working architecture for this feature is a Flask modular monolith with service boundaries inside one codebase, even if broader future evolution is discussed elsewhere.
