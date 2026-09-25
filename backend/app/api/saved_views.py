from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.auth.authorization import require_membership
from app.db.session import get_db
from app.models import Membership
from app.schemas.saved_view import (
    SavedViewCreate,
    SavedViewListResponse,
    SavedViewResponse,
    SavedViewUpdate,
)
from app.services.saved_views import (
    create_saved_view,
    get_saved_view,
    list_saved_views,
    update_saved_view,
)

router = APIRouter(prefix="/organizations/{organization_id}/saved-views", tags=["saved-views"])


@router.get("", response_model=SavedViewListResponse)
def list_all(
    organization_id: UUID,
    membership: Membership = Depends(require_membership),
    db: Session = Depends(get_db),
    entity_type: str | None = Query(default=None, max_length=32),
) -> SavedViewListResponse:
    items = list_saved_views(
        db,
        organization_id=organization_id,
        owner_user_id=membership.user_id,
        entity_type=entity_type,
    )
    return SavedViewListResponse(
        items=[SavedViewResponse.model_validate(item) for item in items]
    )


@router.post("", response_model=SavedViewResponse, status_code=status.HTTP_201_CREATED)
def create(
    organization_id: UUID,
    payload: SavedViewCreate,
    membership: Membership = Depends(require_membership),
    db: Session = Depends(get_db),
) -> SavedViewResponse:
    try:
        view = create_saved_view(
            db,
            organization_id=organization_id,
            owner_user_id=membership.user_id,
            entity_type=payload.entity_type,
            name=payload.name,
            filters=payload.filters,
            columns=payload.columns,
        )
        db.commit()
    except (ValueError, IntegrityError) as exc:
        db.rollback()
        code = status.HTTP_413_REQUEST_ENTITY_TOO_LARGE if isinstance(exc, ValueError) else status.HTTP_409_CONFLICT
        raise HTTPException(status_code=code, detail=str(exc)) from exc
    return SavedViewResponse.model_validate(view)


@router.get("/{view_id}", response_model=SavedViewResponse)
def get(
    organization_id: UUID,
    view_id: UUID,
    membership: Membership = Depends(require_membership),
    db: Session = Depends(get_db),
) -> SavedViewResponse:
    view = get_saved_view(
        db,
        organization_id=organization_id,
        owner_user_id=membership.user_id,
        view_id=view_id,
    )
    if view is None:
        raise HTTPException(status_code=404, detail="Saved view not found")
    return SavedViewResponse.model_validate(view)


@router.patch("/{view_id}", response_model=SavedViewResponse)
def update(
    organization_id: UUID,
    view_id: UUID,
    payload: SavedViewUpdate,
    membership: Membership = Depends(require_membership),
    db: Session = Depends(get_db),
) -> SavedViewResponse:
    view = get_saved_view(
        db,
        organization_id=organization_id,
        owner_user_id=membership.user_id,
        view_id=view_id,
    )
    if view is None:
        raise HTTPException(status_code=404, detail="Saved view not found")
    try:
        values = payload.model_dump(exclude_unset=True)
        view = update_saved_view(
            db,
            view=view,
            name=values.get("name"),
            filters=values.get("filters"),
            columns=values.get("columns"),
        )
        db.commit()
    except (ValueError, IntegrityError) as exc:
        db.rollback()
        code = status.HTTP_413_REQUEST_ENTITY_TOO_LARGE if isinstance(exc, ValueError) else status.HTTP_409_CONFLICT
        raise HTTPException(status_code=code, detail=str(exc)) from exc
    return SavedViewResponse.model_validate(view)


@router.delete("/{view_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete(
    organization_id: UUID,
    view_id: UUID,
    membership: Membership = Depends(require_membership),
    db: Session = Depends(get_db),
) -> Response:
    view = get_saved_view(
        db,
        organization_id=organization_id,
        owner_user_id=membership.user_id,
        view_id=view_id,
    )
    if view is None:
        raise HTTPException(status_code=404, detail="Saved view not found")
    db.delete(view)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
