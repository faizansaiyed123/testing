# Fieldline CRM

A production-minded Small Business CRM focused on keeping customer relationships, opportunities, and follow-ups moving.

> Development is incremental by design: each coherent capability is tested, reviewed, committed, and pushed independently.

## Current state

The repository is in the foundation phase. See `PROJECT_STATUS.md`, `ROADMAP.md`, `ARCHITECTURE.md`, and `DECISIONS.md` for the verified state.

## Technology direction

- Backend: Python, FastAPI, PostgreSQL, SQLAlchemy 2, Alembic
- Frontend: Next.js App Router, React, TypeScript
- Testing: pytest/httpx and Playwright
- Deployment: container-friendly, with no paid service required

## Product principles

1. Answer “what needs attention today?” rather than only reporting totals.
2. Keep prioritization explainable from observable CRM signals.
3. Enforce authorization on the backend.
4. Protect customer history and relationships during data-quality workflows.
5. Keep automation deterministic, auditable, and honest about what it is.
6. Keep `main` stable and build through small, meaningful changes.

## Development

See `docs/` and the project-state files for architecture, roadmap, decisions, and recovery information.
