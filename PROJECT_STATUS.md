# Project Status

**Product:** Fieldline CRM  
**Repository:** `faizansaiyed123/testing`  
**Working branch:** `feature/standout-crm`  
**Stable branch:** `main`  
**Status date:** 2026-09-25

## Verified foundation on main

The CRM core and frontend workspace are already merged into `main`, including:
- multi-tenant FastAPI + PostgreSQL
- secure authentication/session lifecycle with refresh rotation and CSRF binding
- tenant/role authorization and rate limiting
- companies, contacts, opportunities, pipeline, tasks, activities, audit events
- Customer 360 timeline
- explainable attention queue
- idempotent workflow automation
- transaction-safe CSV import
- saved views
- relationship health
- responsive Next.js frontend with public landing, auth, dashboard, contacts, pipeline, saved views, and imports

## Standout expansion in PR #13

Selected after comparing documented CRM patterns across mainstream products and self-hosted/open-source systems. The goal is 4–7 deep additions, not a feature-count race.

### 1. Data Quality Center + safe duplicate merge
- PostgreSQL `pg_trgm` candidate generation for fuzzy names.
- Exact email/phone/website matching where available.
- Explainable duplicate reasons.
- Severity-based data-quality issue ledger.
- Transactional contact/company merge.
- Relationship re-parenting for contacts, opportunities, activities, and tasks.
- Soft deletion of merged records.
- Idempotent merge guard and audit events.

### 2. Daily Work Planner
- Composes existing attention signals with stuck-opportunity detection.
- Deterministic priority.
- Explicit evidence.
- Concrete next action.
- No external AI service.

### 3. Pipeline stuck-opportunity detection
- Configurable stage-aging threshold.
- Configurable activity-inactivity threshold.
- Expected-close proximity.
- Overdue task detection.
- Missing-next-action detection.
- Human-readable reasons and recommended action.

### 4. Observable workflow execution
- Admin-only execution history.
- Workflow name, trigger, event key, action, status, result, timestamps.
- Existing idempotent execution records become inspectable instead of invisible.

### 5. Configurable business rules
- Per-organization inactivity/stage-aging thresholds.
- Admin-only changes.
- Values are consumed by attention and planning logic immediately.

### 6. Relationship graph
- Tenant-scoped contact graph data.
- Company/opportunity/task/activity edges.
- Local SVG rendering in the frontend.
- No external graph service required.

### 7. Self-diagnostic admin health
- Database connectivity.
- Alembic migration version.
- `pg_trgm` availability.
- Incomplete automation-run detection.
- No secrets exposed.

## Verification status for PR #13

Backend:
- Ruff: green on the latest validated head.
- Python compilation: green.
- Alembic migration `0012_standout`: green on PostgreSQL 18.
- Standout backend integration suite: green on the validated head.
- Full current-head run remains the final merge gate after the latest frontend/browser additions.

Frontend:
- TypeScript typecheck: green on the validated standout head.
- Next.js production build: green.
- Existing browser smoke suite: green.
- New standout browser tests cover Data Quality, Daily Planner, Relationship Graph, and Rules/Health surfaces.

E2E:
- PostgreSQL startup, migrations, backend startup, frontend install, and frontend build have all been exercised on the standout branch.
- The real-browser Chromium step is the remaining live gate on the latest head.

## Research basis

The selected architecture emphasizes patterns documented in CRM products such as duplicate management, matching rules, prioritized next actions, activity chaining, configurable workflows, saved views, auditability, and self-hosting. The implementation deliberately keeps these ideas self-contained and deterministic.

## Recovery rule

Before resuming after interruption, inspect Git refs, PR state, commits, migrations, tests, and existing implementation. Never recreate completed work or rewrite useful history.

Never mark a feature verified unless its relevant code path and tests have actually been exercised.
