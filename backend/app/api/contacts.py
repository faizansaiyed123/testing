from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.auth.authorization import require_membership
from app.db.session import get_db
from app.models import Membership
from app.schemas.contact import ContactCreate, ContactListResponse, ContactResponse, ContactUpdate
from app.services.contact import (
    archive_contact,
    create_contact,
    get_contact,
    search_contacts,
    update_contact,
)

router = APIRouter(prefix="/organizations/{organization_id}/contacts", tags=["contacts"])


@router.post("", response_model=ContactResponse, status_code=status.HTTP_201_CREATED)
def create(
    organization_id: UUID,
    payload: ContactCreate,
    membership: Membership = Depends(require_membership),
    db: Session = Depends(get_db),
) -> ContactResponse:
    try:
        contact = create_contact(
            db,
            organization_id=organization_id,
            actor_user_id=membership.user_id,
            first_name=payload.first_name,
            last_name=payload.last_name,
            email=payload.email,
            phone=payload.phone,
            job_title=payload.job_title,
            lifecycle=payload.lifecycle,
            company_id=payload.company_id,
        )
        db.commit()
    except (ValueError, IntegrityError) as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST if isinstance(exc, ValueError) else status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc
    return ContactResponse.model_validate(contact)
