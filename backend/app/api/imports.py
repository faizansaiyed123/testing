from pathlib import Path
from uuid import UUID

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth.authorization import require_membership
from app.db.session import get_db
from app.models import ImportJob, Membership
from app.schemas.imports import ImportPreviewResponse, ImportResponse
from app.services.imports import (
    MAX_BYTES,
    commit_contact_import,
    preview_contacts,
)

router = APIRouter(prefix="/organizations/{organization_id}/imports", tags=["imports"])


def _response(job: ImportJob) -> ImportResponse:
    return ImportResponse(
        id=job.id,
        entity_type=job.entity_type,
        status=job.status,
        filename=job.filename,
        total_rows=job.total_rows,
        valid_rows=job.valid_rows,
        invalid_rows=job.invalid_rows,
        imported_rows=job.imported_rows,
        skipped_rows=job.skipped_rows,
        errors=job.errors,
        completed_at=job.completed_at,
    )


@router.post("/contacts/preview", response_model=ImportPreviewResponse)
async def preview_contacts_csv(
    organization_id: UUID,
    file: UploadFile = File(...),
    membership: Membership = Depends(require_membership),
    db: Session = Depends(get_db),
) -> ImportPreviewResponse:
    filename = Path(file.filename or "contacts.csv").name
    if not filename.lower().endswith(".csv"):
        raise HTTPException(status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, detail="Only CSV files are supported")

    content = await file.read(MAX_BYTES + 1)
    if len(content) > MAX_BYTES:
        raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail="CSV file is too large")

    try:
        job = preview_contacts(
            db,
            organization_id=organization_id,
            user_id=membership.user_id,
            filename=filename,
            content=content,
        )
        db.commit()
    except ValueError as exc:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    return ImportPreviewResponse(**_response(job).model_dump())


@router.get("/{job_id}", response_model=ImportResponse)
def get_import(
    organization_id: UUID,
    job_id: UUID,
    membership: Membership = Depends(require_membership),
    db: Session = Depends(get_db),
) -> ImportResponse:
    job = db.scalar(
        select(ImportJob)
        .where(ImportJob.organization_id == organization_id)
        .where(ImportJob.created_by_user_id == membership.user_id)
        .where(ImportJob.id == job_id)
        .limit(1)
    )
    if job is None:
        raise HTTPException(status_code=404, detail="Import job not found")
    return _response(job)


@router.post("/{job_id}/commit", response_model=ImportResponse)
def commit_import(
    organization_id: UUID,
    job_id: UUID,
    membership: Membership = Depends(require_membership),
    db: Session = Depends(get_db),
) -> ImportResponse:
    job = db.scalar(
        __import__("sqlalchemy").select(ImportJob)
        .where(ImportJob.organization_id == organization_id)
        .where(ImportJob.created_by_user_id == membership.user_id)
        .where(ImportJob.id == job_id)
        .limit(1)
    )
    if job is None:
        raise HTTPException(status_code=404, detail="Import job not found")

    try:
        job = commit_contact_import(
            db,
            job=job,
            actor_user_id=membership.user_id,
        )
    except ValueError as exc:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    return _response(job)
