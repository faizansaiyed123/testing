# Project Status

**Product:** Fieldline CRM  
**Repository:** `faizansaiyed123/testing`  
**Branch:** `main`  
**Status date:** 2026-09-25

## Verified

- GitHub connection is active with push/admin access.
- `main` is the stable branch.
- Product foundation and architecture decisions are documented.
- Backend FastAPI scaffold is implemented.
- PostgreSQL configuration and Alembic migration wiring are implemented.
- Identity schema is implemented: organizations, users, memberships, roles, uniqueness, and indexes.
- Authentication is implemented: Argon2 password hashing, signed short-lived access tokens, opaque refresh sessions, refresh rotation, CSRF checks, secure-cookie production validation, and authenticated `/me`.
- Local backend security/unit tests pass: 12 tests.
- Backend bytecode compilation passes.
- Alembic offline SQL generation includes the identity and auth-session migrations.
- Incremental commits are being pushed to `main` as coherent engineering units.

## Current phase

**Phase 1 — identity and authentication foundation**

Completed slices:
1. product foundation and engineering rules
2. FastAPI backend scaffold
3. PostgreSQL/SQLAlchemy configuration and migration infrastructure
4. organization/user identity model
5. password hashing and token primitives
6. authentication flows and session storage
7. authentication regression tests
8. CI baseline

Next:
1. backend authorization dependencies and role checks
2. rate limiting / brute-force protection for authentication endpoints
3. security headers and structured error handling
4. customer/company domain
5. customer activity/timeline

## Authentication design

- Passwords are stored only as Argon2 hashes.
- Access tokens are short-lived signed JWTs with issuer, audience, type, subject, issued-at, and expiry claims.
- Refresh tokens are random opaque values; only SHA-256 hashes are stored server-side.
- Refresh-token sessions are rotated and locked during rotation to avoid concurrent reuse.
- Refresh/logout require a double-submit CSRF token and bind it to the stored session hash.
- Production configuration requires a non-default JWT secret of at least 32 bytes and secure cookies.
- Refresh cookies use an HttpOnly flag; the CSRF cookie is readable by browser JavaScript so it can be echoed in a request header.

## Environment limitations

The execution container currently has no Docker/PostgreSQL client and does not have the `psycopg` or Ruff packages installed. Package installation from the external package index is blocked by the execution environment's network configuration. Consequently, live PostgreSQL connectivity, live migration execution, Ruff execution, and full GitHub Actions verification remain **blocked/unverified** here.

The CI workflow is configured to run against PostgreSQL 18 and is the authoritative live database quality gate once GitHub Actions executes it.

## Product scope

Fieldline focuses on:
- Customer 360 timeline
- explainable attention/follow-up signals
- duplicate detection and safe merge
- deterministic workflow automation
- transaction-safe CSV import
- saved views and advanced search
- explainable relationship health
- audit history

The system is intentionally designed as a modular monolith until measured requirements justify additional infrastructure.

## Rule

Never mark a feature “verified” unless its relevant code path and tests have actually been exercised.
