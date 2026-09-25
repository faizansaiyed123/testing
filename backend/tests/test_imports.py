from importlib.util import find_spec

import pytest
from sqlalchemy import func, select

from app.auth.crypto import hash_password
from app.auth.tokens import create_access_token
from app.models import Contact, Membership, MembershipRole, Organization, User

POSTGRES_DRIVER_AVAILABLE = find_spec("psycopg") is not None


def _identity(db_session, suffix: str):
    organization = Organization(
        name=f"Import Org {suffix}",
        slug=f"import-{suffix}",
    )
    user = User(
        email=f"import-{suffix}@example.com",
        full_name="Import User",
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
def test_contact_csv_preview_commit_and_summary(client, db_session) -> None:
    organization, user = _identity(db_session, str(id(db_session)))
    existing = Contact(
        organization=organization,
        owner_user_id=user.id,
        first_name="Existing",
        last_name="Customer",
        email="existing@example.com",
    )
    db_session.add(existing)
    db_session.flush()

    csv_data = (
        "first_name,last_name,email,phone,job_title,lifecycle,company_id\n"
        "Ada,Lovelace,ada@example.com,+91 99999 12345,Engineer,prospect,\n"
        "Grace,,grace@example.com,,,lead,\n"
        "Existing,Customer,EXISTING@example.com,,,lead,\n"
        "Alan,Turing,alan@example.com,,,invalid,\n"
    ).encode()

    token = create_access_token(user.id)
    headers = {"Authorization": f"Bearer {token}"}
    preview = client.post(
        f"/api/v1/organizations/{organization.id}/imports/contacts/preview",
        files={"file": ("contacts.csv", csv_data, "text/csv")},
        headers=headers,
    )

    assert preview.status_code == 200
    job = preview.json()
    job_id = job["id"]
    assert job["total_rows"] == 4
    assert job["valid_rows"] == 1
    assert job["invalid_rows"] == 3

    committed = client.post(
        f"/api/v1/organizations/{organization.id}/imports/{job_id}/commit",
        headers=headers,
    )
    assert committed.status_code == 200
    summary = committed.json()
    assert summary["imported_rows"] == 1
    assert summary["skipped_rows"] == 3
    assert summary["status"] == "completed_with_errors"

    ada = db_session.scalar(
        select(Contact)
        .where(Contact.organization_id == organization.id)
        .where(func.lower(Contact.email) == "ada@example.com")
    )
    assert ada is not None
    assert ada.first_name == "Ada"
    assert ada.lifecycle == "prospect"

    fetched = client.get(
        f"/api/v1/organizations/{organization.id}/imports/{job_id}",
        headers=headers,
    )
    assert fetched.status_code == 200
    assert fetched.json()["imported_rows"] == 1

    reused = client.post(
        f"/api/v1/organizations/{organization.id}/imports/{job_id}/commit",
        headers=headers,
    )
    assert reused.status_code == 409


@pytest.mark.skipif(
    not POSTGRES_DRIVER_AVAILABLE,
    reason="PostgreSQL driver is required for integration tests",
)
def test_import_job_is_owner_scoped(client, db_session) -> None:
    organization, user = _identity(db_session, f"owner-{id(db_session)}")
    other = User(
        email=f"import-other-{id(client)}@example.com",
        full_name="Other User",
        password_hash=hash_password("Correct Horse Battery Staple"),
    )
    db_session.add(other)
    db_session.flush()
    db_session.add(
        Membership(
            organization_id=organization.id,
            user_id=other.id,
            role=MembershipRole.MEMBER,
        )
    )
    db_session.flush()

    token = create_access_token(user.id)
    other_token = create_access_token(other.id)
    preview = client.post(
        f"/api/v1/organizations/{organization.id}/imports/contacts/preview",
        files={
            "file": (
                "contacts.csv",
                b"first_name,last_name,email\nTest,User,test@example.com\n",
                "text/csv",
            )
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert preview.status_code == 200
    job_id = preview.json()["id"]

    response = client.get(
        f"/api/v1/organizations/{organization.id}/imports/{job_id}",
        headers={"Authorization": f"Bearer {other_token}"},
    )
    assert response.status_code == 404
