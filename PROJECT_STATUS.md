# Project Status

**Product:** Fieldline CRM  
**Repository:** `faizansaiyed123/testing`  
**Working branch:** `feature/automation`  
**Stable branch:** `main`  
**Status date:** 2026-09-25

## Backend slices in this cumulative branch

- FastAPI backend scaffold with versioned routing and OpenAPI.
- PostgreSQL/SQLAlchemy configuration and Alembic migration infrastructure.
- Organization, user, membership, and role identity model.
- Argon2 password hashing and secure authentication lifecycle.
- Short-lived signed access JWTs with issuer/audience/type/expiry validation.
- Opaque refresh sessions with server-side hashes, rotation, locking, CSRF binding, and secure-cookie production checks.
- Tenant membership and reusable role authorization dependencies.
- Database-backed authentication throttling with HMAC fingerprints.
- CRM core schema: companies, contacts, pipeline stages, opportunities, activities, tasks, and audit events.
- Tenant-scoped audited company/contact CRUD, search, archive, and cross-tenant validation.
- Stage-driven opportunity state with explicit win/loss invariants.
- Customer 360 timeline using SQL `UNION ALL` with bounded cursor pagination.
- HTTP request IDs, safe internal errors, security headers, auth cache prevention, and DB readiness.
- Default sales pipeline stages during organization signup.
- Explainable attention queue for overdue work, overdue open opportunities, stale open opportunities, and stale lead/prospect relationships.
- Deterministic workflow automation: admin-managed rules, opportunity transition triggers, transaction-scoped task creation, execution records, unique event keys, idempotency, and task audit events.

## Current GitHub review state

The repository already contains several older feature branches/PRs that were created independently from earlier repository states. They are not being treated as authoritative.

The cumulative branch `feature/automation` is the intended continuation because it contains the current linear backend implementation from the CRM foundation through attention and automation.

A new PR from this branch is the authoritative merge candidate. It must pass the exact-head GitHub Actions gate before `main` is changed.

## Automation contract

Supported deterministic triggers:
- `opportunity.won`
- `opportunity.lost`

Supported action:
- `create_task`

Execution is idempotent by `rule_id + event_key`. The event key includes opportunity id, previous status, new status, and target stage id. Duplicate delivery of the same transition does not create a second task.

Automation rule creation and enable/disable operations are restricted to organization owners/admins. Automation-generated tasks retain normal CRM ownership, relationship links, and audit history.

## Verification state

GitHub Actions has successfully demonstrated PostgreSQL service startup, backend installation, source linting, Python compilation, and live Alembic execution on recent backend runs. Test failures found during development were inspected and corrected rather than bypassed.

The current cumulative head still requires its own exact-head CI run because the branch has advanced since prior checks.

The local execution container cannot provide live PostgreSQL/Ruff verification, so no local live-DB pass is claimed.

## Next slices after merge

1. Finish exact-head CI for the cumulative backend branch and merge it into `main`.
2. Transaction-safe CSV import with dry-run, validation, rollback, and row-level error reporting.
3. Saved views / advanced search / relationship health.
4. Frontend foundation and real API integration.
5. Full end-to-end, accessibility, security, performance, and repository audit.

## Recovery rule

Before resuming after interruption, inspect Git refs, PR state, commits, migrations, tests, and existing implementation. Never recreate completed work or rewrite useful history.

Never mark a feature verified unless its relevant code path and tests have actually been exercised.
