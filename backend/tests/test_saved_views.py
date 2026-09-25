from importlib.util import find_spec

import pytest

from app.auth.crypto import hash_password
from app.auth.tokens import create_access_token
from app.models import Membership, MembershipRole, Organization, User

POSTGRES_DRIVER_AVAILABLE = find_spec("psycopg") is not None


def _identity(db_session, suffix: str):
    organization = Organization(name=f"Views Org {suffix}", slug=f"views-{suffix}")
    user = User(
        email=f"views-{suffix}@example.com",
        full_name="Views User",
        password_hash=hash_password("Correct Horse Battery Staple"),
    )
    membership = Membership(
        organization=organization,
        user=user,
        role=MembershipRole.OWNER,
    )
    db_session.add_all([organization, user, membership])
    db_session.flush()
    return organization, user


@pytest.mark.skipif(
    not POSTGRES_DRIVER_AVAILABLE,
    reason="PostgreSQL driver is required for integration tests",
)
def test_saved_view_crud_and_owner_isolation(client, db_session) -> None:
    organization, user = _identity(db_session, str(id(db_session)))
    other_user = User(
        email=f"other-{id(client)}@example.com",
        full_name="Other User",
        password_hash=hash_password("Correct Horse Battery Staple"),
    )
    db_session.add(other_user)
    db_session.flush()
    db_session.add(
        Membership(
            organization_id=organization.id,
            user_id=other_user.id,
            role=MembershipRole.MEMBER,
        )
    )
    db_session.flush()

    token = create_access_token(user.id)
    other_token = create_access_token(other_user.id)
    base = f"/api/v1/organizations/{organization.id}/saved-views"

    created = client.post(
        base,
        json={
            "entity_type": "opportunity",
            "name": "Needs Attention",
            "filters": {"status": "open", "min_amount": 5000},
            "columns": ["name", "amount", "stage"],
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert created.status_code == 201
    view = created.json()
    view_id = view["id"]

    duplicate = client.post(
        base,
        json={
            "entity_type": "opportunity",
            "name": "needs attention",
            "filters": {},
            "columns": [],
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert duplicate.status_code == 409

    listed = client.get(
        f"{base}?entity_type=opportunity",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert listed.status_code == 200
    assert listed.json()["items"][0]["id"] == view_id

    hidden = client.get(
        f"{base}/{view_id}",
        headers={"Authorization": f"Bearer {other_token}"},
    )
    assert hidden.status_code == 404

    updated = client.patch(
        f"{base}/{view_id}",
        json={"filters": {"status": "won"}},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert updated.status_code == 200
    assert updated.json()["filters"] == {"status": "won"}

    too_large = client.post(
        base,
        json={
            "entity_type": "contact",
            "name": "Huge",
            "filters": {f"key_{i}": "x" * 1000 for i in range(20)},
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert too_large.status_code == 413

    deleted = client.delete(
        f"{base}/{view_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert deleted.status_code == 204

    missing = client.get(
        f"{base}/{view_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert missing.status_code == 404


@pytest.mark.skipif(
    not POSTGRES_DRIVER_AVAILABLE,
    reason="PostgreSQL driver is required for integration tests",
)
def test_saved_view_cannot_cross_organizations(client, db_session) -> None:
    first, first_user = _identity(db_session, f"a-{id(db_session)}")
    second, second_user = _identity(db_session, f"b-{id(client)}")

    token = create_access_token(first_user.id)
    foreign_token = create_access_token(second_user.id)
    foreign_base = f"/api/v1/organizations/{second.id}/saved-views"

    client.post(
        foreign_base,
        json={
            "entity_type": "contact",
            "name": "Foreign View",
            "filters": {},
        },
        headers={"Authorization": f"Bearer {foreign_token}"},
    )

    response = client.get(
        foreign_base,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 403
