# Project Status

**Product:** Fieldline CRM  
**Repository:** `faizansaiyed123/testing`  
**Working branch:** `feature/attention-queue`  
**Stable branch:** `main`  
**Status date:** 2026-09-25

## Backend slices completed

- FastAPI backend scaffold with versioned API routing.
- PostgreSQL/SQLAlchemy configuration and Alembic migrations.
- Organization, user, membership, and role identity model.
- Argon2 password hashing.
- Short-lived signed access JWTs with issuer/audience/type/expiry validation.
- Opaque refresh-token sessions with server-side hashes, rotation, locking, CSRF binding, and secure-cookie production checks.
- Tenant membership and reusable role authorization dependencies.
- Database-backed authentication throttling using HMAC fingerprints.
- CRM core schema: companies, contacts, pipeline stages, opportunities, activities, tasks, and audit events.
- Tenant-scoped audited CRUD/search/archive workflows for companies and contacts.
- Stage-driven opportunity state with cross-tenant relationship validation.
- Customer 360 timeline using SQL `UNION ALL` and cursor pagination.
- HTTP request IDs, safe internal-error responses, security headers, auth cache prevention, and database readiness probe.
- Default sales pipeline stages on organization signup.
- Explainable attention queue for overdue tasks, overdue open opportunities, stale open opportunities, and stale lead/prospect contacts.

## Current branch state

`feature/crm-core` remains the CRM foundation branch and PR #1 remains open/unstable; live PostgreSQL CI is the merge gate.

`feature/attention-queue` is branched from the current CRM head and PR #4 is open for the attention queue. Its current head is under GitHub Actions verification.

## Attention queue contract

The queue is deliberately deterministic and evidence-based; it is not presented as AI.

Priority signals:
- 95: overdue incomplete task.
- 90: open opportunity past expected close date.
- 65: open opportunity with no recent activity for 21+ days.
- 70: lead/prospect with no recent activity for 14+ days.

Every item includes the entity type/id, priority, human-readable reason, due timestamp when applicable, and last recorded activity timestamp. Results are tenant-scoped and bounded to a maximum of 100 items.

## Verification state

GitHub Actions has already demonstrated that the backend can install successfully, start PostgreSQL 18, compile, and apply the CRM migration chain through `0007_timeline_indexes`.

Attention branch migration `0008_attention_indexes` is present and will be validated by the current PR run.

The local execution container lacks Docker/PostgreSQL client tooling and external package installation is unavailable, so local live-DB/Ruff verification is not claimed.

## Next engineering slices

1. Finish and merge the attention queue after its exact-head CI passes.
2. Resolve/merge the CRM-core PR without rewriting useful history.
3. Deterministic workflow automation with idempotency and audit trails.
4. Transaction-safe CSV import with validation, dry-run, rollback, and row-level error reporting.
5. Saved views, advanced search, and explainable relationship health.
6. Frontend foundation and real API integration.
7. Full end-to-end, accessibility, security, performance, and final repository audit.

## Recovery rule

Before resuming after interruption, inspect Git refs, PR state, commits, migrations, tests, and existing implementation. Do not recreate completed work or rewrite useful history.

Never mark a feature verified unless its relevant code path and tests have actually been exercised.
