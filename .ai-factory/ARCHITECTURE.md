# Architecture: Modular Monolith

## Overview
For the second part of this project, the working architecture must be a Flask modular monolith, not microservices. The required scope is a single web application with authentication, PostgreSQL persistence, user VK settings, server-rendered pages, and reuse of existing generation/publishing logic.

This architecture fits the current repository and the assignment constraints: one deployable service, one PostgreSQL database, Docker-based VPS deployment, and minimal operational complexity. Existing integrations with OpenAI and VK remain inside the same codebase, but must be wrapped behind clear service boundaries so the Flask web layer does not depend on raw legacy modules directly.

## Decision Rationale
- **Project type:** Flask web application for SMM workflow automation
- **Tech stack:** Python, Flask, PostgreSQL, SQLAlchemy, Jinja, Bootstrap
- **Key factor:** MVP delivery with clear module boundaries, production-minded structure, and reuse of existing business logic without unnecessary infrastructure

## Folder Structure
```text
.
|- app/
|  |- __init__.py                # Flask app factory
|  |- config.py                  # Environment-driven application config
|  |- extensions.py              # SQLAlchemy, LoginManager, CSRF, Migrate
|  |- auth/                      # Registration, login, logout
|  |  |- routes.py
|  |  `- forms.py
|  |- main/                      # Dashboard and general pages
|  |  `- routes.py
|  |- settings/                  # User VK settings UI and persistence
|  |  |- routes.py
|  |  `- forms.py
|  |- content/                   # Post generation workflow
|  |  |- routes.py
|  |  `- forms.py
|  |- stats/                     # VK stats pages
|  |  `- routes.py
|  |- models/                    # SQLAlchemy models
|  |  |- user.py
|  |  |- vk_settings.py
|  |  `- generated_post.py
|  |- services/                  # Application-facing service layer
|  |  |- auth_service.py
|  |  |- settings_service.py
|  |  |- content_workflow.py
|  |  |- vk_service.py
|  |  `- stats_service.py
|  `- templates/                 # Jinja templates with Bootstrap
|- generators/                   # Legacy OpenAI generation logic to reuse/refactor
|- social_publishers/            # Legacy VK/Telegram publisher logic to reuse/refactor
|- social_stats/                 # Legacy statistics logic to reuse/refactor
|- tests/                        # Unit and integration tests
|- migrations/                   # Database migrations if Flask-Migrate is adopted
|- docker/                       # Optional entrypoint/wait scripts
|- Dockerfile
|- docker-compose.yml
|- .env.example
`- README.md
```

## Dependency Rules
- ✅ `app/routes` may depend on `app/forms`, `app/services`, and Flask extensions.
- ✅ `app/services` may depend on `app/models` and legacy integration modules.
- ✅ Legacy integration modules may be refactored internally, but must not import Flask request/session/template concerns.
- ✅ Configuration must flow from environment variables into Flask config and then into services.
- ❌ Blueprints must not call `vk_api`, `openai`, or `requests` directly if that bypasses service-layer validation and error handling.
- ❌ Legacy modules must not configure global logging with `logging.basicConfig()`.
- ❌ Secrets, raw tokens, and passwords must never be embedded in code, templates, logs, or tests.

## Layer and Module Communication
- Blueprints handle HTTP, forms, flash messages, redirects, and template rendering.
- Services orchestrate business actions: registration, settings update, post generation, image generation, VK publication, and VK stats retrieval.
- Models persist user data, VK settings, and generation/publication history.
- Legacy modules remain integration adapters behind service APIs until they are cleaned up.
- Database writes happen in service boundaries, not in templates or raw integration modules.

## VK Integration Rules
- Use a fixed VK API version in the integration layer so response formats do not drift unexpectedly between environments.
- Treat VK publishing as a capability, not a guaranteed feature: validate token, rights, and group access before attempting `wall.post`.
- `wall.post` and wall-photo upload methods currently require user access tokens and restricted rights (`wall`, `photos`), so the app must degrade gracefully when auto-posting is unavailable.
- Auto-post failure must not discard a successfully generated text or image; the user should still receive generated content and a clear UI warning.
- For subscriber count, prefer `groups.getById(fields=members_count)` and keep `groups.getMembers` as a fallback when needed.
- Wrap `groups.getById` behind an adapter because the response format changed in VK API v5.139.

## Key Principles
1. Keep one deployable Flask app with strong internal module boundaries.
2. Reuse existing generation and VK logic where it is sound, but normalize configuration, logging, timeouts, and error handling.
3. Preserve user-facing success whenever possible: generation should succeed independently from optional VK posting.
4. Make all operational behavior environment-driven for Docker/VPS deployment.
5. Prefer explicit, boring, maintainable flows over architectural overreach.

## Code Examples

### Route Delegating to Service Layer
```python
from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app.content.forms import PostGenerationForm
from app.services.content_workflow import ContentWorkflowService

bp = Blueprint("content", __name__)


@bp.route("/generate", methods=["GET", "POST"])
@login_required
def generate():
    form = PostGenerationForm()
    if form.validate_on_submit():
        service = ContentWorkflowService()
        result = service.generate_for_user(
            user=current_user,
            tone=form.tone.data,
            topic=form.topic.data,
            generate_image=form.generate_image.data,
            auto_post_vk=form.auto_post_vk.data,
        )
        if result.vk_warning:
            flash(result.vk_warning, "warning")
        return render_template("content/result.html", result=result)
    return render_template("content/generator.html", form=form)
```

### VK Stats Adapter Boundary
```python
class VKStatsService:
    def __init__(self, vk_client):
        self.vk_client = vk_client

    def get_group_members_count(self, token: str, group_id: int) -> int:
        payload = self.vk_client.get_group_info(
            token=token,
            group_id=group_id,
            fields=["members_count"],
            api_version="5.139",
        )
        return self.vk_client.extract_members_count(payload, fallback_group_id=group_id)
```

## Anti-Patterns
- ❌ Building a separate microservice layout for Flask, VK, and OpenAI during MVP implementation.
- ❌ Calling legacy publishers directly from templates or request handlers.
- ❌ Treating VK auto-post as mandatory and failing the whole generation flow when posting rights are absent.
- ❌ Parsing raw VK responses in multiple places instead of through one service adapter.
- ❌ Mixing demo scripts, CLI checks, and Flask runtime entrypoints in the same execution path.
