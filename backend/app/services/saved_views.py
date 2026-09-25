import json
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import SavedView

MAX_FILTER_BYTES = 16_384


def _validate_size(filters: dict[str, object]) -> None:
    if len(json.dumps(filters, separators=(",", ":"), default=str).encode("utf-8")) > MAX_FILTER_BYTES:
        raise ValueError("Saved view filters are too large")


def get_saved_view(
    db: Session,
    *,
    organization_id: UUID,
    owner_user_id: UUID,
    view_id: UUID,
) -> SavedView | None:
    return db.scalar(
        select(SavedView)
        .where(SavedView.organization_id == organization_id)
        .where(SavedView.owner_user_id == owner_user_id)
        .where(SavedView.id == view_id)
        .limit(1)
    )


def list_saved_views(
    db: Session,
    *,
    organization_id: UUID,
    owner_user_id: UUID,
    entity_type: str | None,
) -> list[SavedView]:
    statement = (
        select(SavedView)
        .where(SavedView.organization_id == organization_id)
        .where(SavedView.owner_user_id == owner_user_id)
    )
    if entity_type:
        statement = statement.where(SavedView.entity_type == entity_type)
    return db.scalars(
        statement.order_by(func.lower(SavedView.name).asc())
    ).all()


def create_saved_view(
    db: Session,
    *,
    organization_id: UUID,
    owner_user_id: UUID,
    entity_type: str,
    name: str,
    filters: dict[str, object],
    columns: list[str],
) -> SavedView:
    _validate_size(filters)
    view = SavedView(
        organization_id=organization_id,
        owner_user_id=owner_user_id,
        entity_type=entity_type,
        name=name,
        filters=filters,
        columns=columns,
    )
    db.add(view)
    db.flush()
    return view


def update_saved_view(
    db: Session,
    *,
    view: SavedView,
    name: str | None,
    filters: dict[str, object] | None,
    columns: list[str] | None,
) -> SavedView:
    if filters is not None:
        _validate_size(filters)
        view.filters = filters
    if name is not None:
        view.name = name
    if columns is not None:
        view.columns = columns
    db.flush()
    return view
