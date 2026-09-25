# Fieldline CRM

A production-minded small-business CRM focused on customer context, pipeline execution, data integrity, and explainable operational intelligence.

> The product is deliberately deeper than CRUD: the system surfaces evidence, protects history, makes automation observable, and keeps tenant boundaries explicit.

## Technology

- Backend: Python, FastAPI, PostgreSQL, SQLAlchemy 2, Alembic
- Frontend: Next.js App Router, React, TypeScript
- Testing: pytest/httpx, Playwright
- Runtime: container-friendly and self-hostable
- External paid services: none required

## Why this CRM stands out

### Explainable operational intelligence

The Data Quality Center, Daily Work Planner, attention queue, and stuck-opportunity detector use deterministic business rules and surface their evidence. The product does not pretend to be an AI system when it is actually a rules engine.

### Safe duplicate merge

Potential duplicate contacts and companies can be reviewed before action. Merges run transactionally, re-parent related activities/tasks/opportunities, soft-delete the merged record, block repeated merges, and write audit events for both sides of the operation.

### Relationship context as a system

Customer 360, relationship health, and the relationship graph expose how a contact connects to companies, opportunities, tasks, and activity instead of treating the contact record as an isolated table row.

### Observable automation

Workflow execution history shows the rule, trigger, event key, status, action type, and result. The backend uses idempotent execution records so repeated delivery of the same event does not create duplicate follow-up work.

### Configurable CRM behavior

Administrators can tune inactivity and stage-aging thresholds without code changes. Those values are consumed directly by attention, planning, and pipeline-intelligence calculations.

### Self-diagnostic operations

The admin console checks database connectivity, migration state, fuzzy-matching capability, and incomplete automation runs without depending on an external monitoring SaaS.

### Transaction-safe data import

CSV imports preview and normalize data, report row-level validation errors, detect duplicates, support dry runs, revalidate before commit, and preserve rollback semantics.

## Product surface

The application includes a public landing page, secure signup/login/session restoration, responsive workspace navigation, dashboard and attention queue, contacts with relationship health, pipeline, saved views, safe CSV import, Data Quality Center, Daily Work Planner, automation history, admin rules/health, stuck-opportunity intelligence, and a local relationship graph.

## Engineering principles

1. Tenant boundaries are enforced on the backend.
2. Important decisions are explainable from observable CRM state.
3. History is preserved through audit events and safe relationship transfers.
4. Automation is deterministic, idempotent, and visible.
5. Production-like PostgreSQL integration tests are part of the merge gate.
6. Browser verification covers the real frontend surface.

See `PROJECT_STATUS.md`, `ARCHITECTURE.md`, `ROADMAP.md`, and `DECISIONS.md` for implementation details and recovery notes.
