# Project: SMS Assistant

## Overview
Python application for generating social media content with OpenAI, publishing it to VK and Telegram, and collecting basic delivery statistics from those platforms.

## Core Features
- Generate post text with OpenAI chat models.
- Generate post images with OpenAI image models.
- Publish text and image posts to VK communities.
- Send text and image posts to Telegram chats or channels.
- Collect basic VK and Telegram post statistics.
- Verify environment configuration and run automated tests.

## Tech Stack
- **Language:** Python 3.8+
- **Runtime/Packaging:** `requirements.txt`
- **Framework:** Flask
- **Database:** PostgreSQL
- **ORM:** Flask-SQLAlchemy / SQLAlchemy
- **Testing:** `pytest`, `pytest-cov`, `pytest-mock`
- **Logging:** `loguru`, standard `logging`
- **External APIs:** OpenAI, VK API, Telegram Bot API
- **HTTP:** `requests`
- **Configuration:** environment variables via `.env`

## Existing Structure
- `app/` contains the Flask app factory, blueprints, services, and templates.
- `generators/` contains content generation modules.
- `social_publishers/` contains platform-specific publishing adapters.
- `social_stats/` contains platform statistics collection.
- `tests/` contains unit and integration tests.
- `Dockerfile`, `docker-compose.yml`, and `docker/entrypoint.sh` provide containerized deployment for VPS.
- `test.py`, `test_env.py`, and `run_tests.py` remain legacy/demo-oriented scripts pending further cleanup.

## Architecture Notes
- Current architecture is a small modular monolith organized by responsibility.
- Platform integrations are separated into focused modules instead of a shared service layer.
- Configuration is expected to come from environment-driven runtime settings.
- The project currently uses direct SDK/API clients inside modules rather than explicit interface abstractions.

## Architecture
See `.ai-factory/ARCHITECTURE.md` for detailed architecture guidelines.
Pattern: Modular Monolith

## Non-Functional Requirements
- Logging should remain configurable via `LOG_LEVEL`.
- Secrets must stay in environment variables and never be committed.
- External API failures should be handled explicitly and logged without leaking credentials.
- Tests should remain runnable through `pytest` and `run_tests.py`.
