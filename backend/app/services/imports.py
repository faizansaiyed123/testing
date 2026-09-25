import csv
import io
from collections.abc import Iterable
from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models import Company, Contact, ImportJob

MAX_BYTES = 5 * 1024 * 1024
MAX_ROWS = 5000
REQUIRED_HEADERS = {"first_name", "last_name"}
ALLOWED_HEADERS = {
    "first_name",
    "last_name",
    "email",
    "phone",
    "job_title",
    "lifecycle",
    "company_id",
}


def _normalize_text(value: str | None) -> str | None:
    if value is None:
        return None
    value = " ".join(value.split())
    return value or None


def _normalize_email(value: str | None) -> str | None:
    value = _normalize_text(value)
    return value.lower() if value else None


def _parse_csv(content: bytes) -> list[dict[str, str]]:
    if len(content) > MAX_BYTES:
        raise ValueError("CSV file is too large")
    try:
        text = content.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise ValueError("CSV must be UTF-8 encoded") from exc

    reader = csv.DictReader(io.StringIO(text, newline=""))
    headers = {header.strip() for header in (reader.fieldnames or []) if header}
    if not REQUIRED_HEADERS <= headers:
        missing = ", ".join(sorted(REQUIRED_HEADERS - headers))
        raise ValueError(f"Missing required CSV headers: {missing}")
    unknown = headers - ALLOWED_HEADERS
    if unknown:
        raise ValueError(f"Unsupported CSV headers: {', '.join(sorted(unknown))}")

    rows: list[dict[str, str]] = []
    for index, row in enumerate(reader, start=2):
        if index - 1 > MAX_ROWS:
            raise ValueError(f"CSV contains more than {MAX_ROWS} data rows")
        rows.append({key.strip(): (value or "") for key, value in row.items() if key})
    return rows


def _validate_row(
    row: dict[str, str],
    *,
    organization_id: UUID,
    db: Session,
) -> tuple[dict[str, object], list[str]]:
    errors: list[str] = []
    first_name = _normalize_text(row.get("first_name"))
    last_name = _normalize_text(row.get("last_name"))
    email = _normalize_email(row.get("email"))
    phone = _normalize_text(row.get("phone"))
    job_title = _normalize_text(row.get("job_title"))
    lifecycle = _normalize_text(row.get("lifecycle")) or "lead"
    company_id_raw = _normalize_text(row.get("company_id"))

    if not first_name:
        errors.append("first_name is required")
    if not last_name:
        errors.append("last_name is required")
    if lifecycle not in {"lead", "prospect", "customer", "churned"}:
        errors.append("lifecycle must be lead, prospect, customer, or churned")

    company_id = None
    if company_id_raw:
        try:
            company_id = UUID(company_id_raw)
        except ValueError:
            errors.append("company_id must be a UUID")
        else:
            exists = db.scalar(
                select(Company.id)
                .where(Company.organization_id == organization_id)
                .where(Company.id == company_id)
                .where(Company.deleted_at.is_(None))
                .limit(1)
            )
            if exists is None:
                errors.append("company_id does not belong to this organization")

    normalized = {
        "first_name": first_name,
        "last_name": last_name,
        "email": email,
        "phone": phone,
        "job_title": job_title,
        "lifecycle": lifecycle,
        "company_id": company_id,
    }
    return normalized, errors


def preview_contacts(
    db: Session,
    *,
    organization_id: UUID,
    user_id: UUID,
    filename: str,
    content: bytes,
) -> ImportJob:
    raw_rows = _parse_csv(content)
    staged_rows: list[dict[str, object]] = []
    errors: list[dict[str, object]] = []
    valid_rows = 0
    seen_emails: set[str] = set()

    for row_number, raw in enumerate(raw_rows, start=2):
        normalized, row_errors = _validate_row(raw, organization_id=organization_id, db=db)
        email = normalized["email"]
        if isinstance(email, str):
            if email in seen_emails:
                row_errors.append("duplicate email within import")
            seen_emails.add(email)
            existing = db.scalar(
                select(Contact.id)
                .where(Contact.organization_id == organization_id)
                .where(func.lower(Contact.email) == email)
                .where(Contact.deleted_at.is_(None))
                .limit(1)
            )
            if existing is not None:
                row_errors.append("email already exists")
        if row_errors:
            errors.append({"row_number": row_number, "errors": row_errors})
        else:
            valid_rows += 1
        staged_rows.append({"row_number": row_number, "data": normalized})

    job = ImportJob(
        organization_id=organization_id,
        created_by_user_id=user_id,
        entity_type="contacts",
        status="previewed",
        filename=filename,
        total_rows=len(raw_rows),
        valid_rows=valid_rows,
        invalid_rows=len(errors),
        imported_rows=0,
        skipped_rows=0,
        rows=staged_rows,
        errors=errors,
    )
    db.add(job)
    db.flush()
    return job


def commit_contact_import(
    db: Session,
    *,
    job: ImportJob,
    actor_user_id: UUID,
) -> ImportJob:
    if job.status != "previewed":
        raise ValueError("Import job is already completed")

    imported = 0
    skipped = 0
    errors = list(job.errors)

    for item in job.rows:
        row_number = int(item["row_number"])
        data = dict(item["data"])
        if any(error["row_number"] == row_number for error in errors):
            skipped += 1
            continue
        try:
            with db.begin_nested():
                contact = Contact(
                    organization_id=job.organization_id,
                    owner_user_id=actor_user_id,
                    **data,
                )
                db.add(contact)
                db.flush()
            imported += 1
        except IntegrityError:
            skipped += 1
            errors.append(
                {"row_number": row_number, "errors": ["contact conflicts with existing data"]}
            )

    job.imported_rows = imported
    job.skipped_rows = skipped
    job.errors = errors
    job.status = "imported" if not errors else "completed_with_errors"
    job.completed_at = datetime.now(UTC)
    db.commit()
    return job
