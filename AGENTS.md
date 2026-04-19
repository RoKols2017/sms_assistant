# AGENTS.md

> Project map for AI agents. Keep this file up-to-date as the project evolves.

## Project Overview
Python project for generating SMM content with OpenAI, publishing it to VK and Telegram, and collecting basic social media statistics. See `.ai-factory/DESCRIPTION.md` for the fuller project specification.

## Tech Stack
- **Language:** Python
- **Framework:** Flask
- **Database:** PostgreSQL
- **ORM:** SQLAlchemy

## Project Structure
```text
.
|- app/                      # Flask app factory, blueprints, services, models, templates
|- generators/               # OpenAI-backed text and image generation modules
|- social_publishers/        # VK and Telegram publishing adapters
|- social_stats/             # Platform statistics collection
|- tests/                    # Unit and integration test suite
|- docker/                   # Container entrypoint and deploy helpers
|- .cursor/                  # Editor-specific project rules
|- .opencode/                # Local AI skills and tool metadata
|- README.md                 # User-facing project overview and usage
|- requirements.txt          # Python dependencies
|- pytest.ini                # Pytest configuration and coverage thresholds
|- run_tests.py              # Test runner helper
|- test.py                   # End-to-end demo script
|- test_env.py               # Environment validation script
|- .env.example              # Example environment variables
|- Dockerfile                # Web container build
|- docker-compose.yml        # Web + PostgreSQL stack
|- wsgi.py                   # WSGI entrypoint for Gunicorn
|- .mcp.json                 # MCP server configuration for AI tooling
`- .ai-factory/              # AI Factory project context files
```

## Key Entry Points
| File | Purpose |
|------|---------|
| `app/__init__.py` | Creates and configures the Flask application |
| `app/config.py` | Defines Flask runtime configuration classes |
| `app/services/content_workflow.py` | Orchestrates generation and optional VK posting |
| `app/services/stats_service.py` | Reads VK stats for the signed-in user |
| `test.py` | Runs the demo workflow: generate content, publish, then collect stats |
| `test_env.py` | Validates required environment variables and setup |
| `run_tests.py` | Convenience entry point for the test suite |
| `generators/text_gen.py` | Generates post text through OpenAI chat completions |
| `generators/image_gen.py` | Generates images through OpenAI image APIs |
| `social_publishers/vk_publisher.py` | Publishes posts to VK |
| `social_publishers/telegram_publisher.py` | Sends posts to Telegram |
| `social_stats/stats_collector.py` | Collects VK and Telegram statistics |
| `requirements.txt` | Declares runtime and test dependencies |
| `pytest.ini` | Defines pytest discovery and coverage settings |

## Documentation
| Document | Path | Description |
|----------|------|-------------|
| README | `README.md` | Project landing page |
| Getting Started | `docs/getting-started.md` | Local and VPS startup |
| Configuration | `docs/configuration.md` | Flask, OpenAI, and Postgres env |
| VK Integration | `docs/vk-integration.md` | VK token types and requirements |
| Architecture | `docs/architecture.md` | Flask modular monolith structure |
| Testing | `docs/testing.md` | Tests and smoke-check commands |
| Security | `docs/security.md` | Secrets and VK token caveats |

## AI Context Files
| File | Purpose |
|------|---------|
| `AGENTS.md` | This file - project structure map |
| `.ai-factory/DESCRIPTION.md` | Project specification and detected stack |
| `.ai-factory/ARCHITECTURE.md` | Architecture decisions and implementation rules |
| `CLAUDE.md` | Claude Code instructions and preferences if added later |
