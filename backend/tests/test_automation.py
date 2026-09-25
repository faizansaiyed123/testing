from datetime import UTC, datetime, timedelta
from importlib.util import find_spec

import pytest
from sqlalchemy import func, select

from app.auth.crypto import hash_password
from app.auth.tokens import create_access_token
from app.models import AuditEvent, Membership, MembershipRole, Opportunity, Organization, PipelineStage, Task, User

POSTGRES_DRIVER_AVAILABLE = find_spec("psycopg") is not None


@pytest.mark.skipif(
    not POSTGRES_DRIVER_AVAILABLE,
    reason="PostgreSQL driver is required for integration tests",
)
def test_stage_change_creates_one_idempotent_follow_up(client, db_session) -> None:
    organization = Organization(
        name="Automation Org",
        slug=f"automation-{id(db_session)}",
    )
    user = User(
        email=f"automation-{id(db_session)}@example.com",
        full_name="Automation User",
        password_hash=hash_password("Correct Horse Battery Staple"),
    )
    membership = Membership(
        organization=organization,
        user=user,
        role=MembershipRole.OWNER,
    )
    first_stage = PipelineStage(
        organization=organization,
        name="New",
        order_index=10,
    )
    second_stage = PipelineStage(
        organization=organization,
        name="Qualified",
        order_index=20,
        win_probability=0.25,
    )
    db_session.add_all(
        [organization, user, membership, first_stage, second_stage],
    )
    db_session.flush()

    opportunity = Opportunity(
        organization=organization,
        owner_user_id=user.id,
        stage=first_stage,
        name="Automation Deal",
    )
    db_session.add(opportunity)
    db_session.flush()

    token = create_access_token(user.id)
    headers = {"Authorization": f"Bearer {token}"}
    url = (
        f"/api/v1/organizations/{organization.id}/opportunities/"
        f"{opportunity.id}"
    )

    response = client.patch(
        url,
        json={"stage_id": str(second_stage.id)},
        headers=headers,
    )
    assert response.status_code == 200

    task = db_session.scalar(
        select(Task)
        .where(Task.opportunity_id == opportunity.id)
        .where(Task.automation_key.is_not(None))
    )
    assert task is not None
    assert task.title == "Follow up on Automation Deal"
    assert task.priority == "high"

    changed_at = opportunity.stage_changed_at
    response = client.patch(
        url,
        json={"stage_id": str(second_stage.id)},
        headers=headers,
    )
    assert response.status_code == 200

    assert db_session.scalar(
        select(func.count())
        .select_from(Task)
        .where(Task.opportunity_id == opportunity.id)
        .where(Task.automation_key.is_not(None))
    ) == 1
    assert opportunity.stage_changed_at >= changed_at

    assert db_session.scalar(
        select(func.count())
        .select_from(AuditEvent)
        .where(AuditEvent.entity_type == "task")
        .where(AuditEvent.entity_id == task.id)
    ) == 1


@pytest.mark.skipif(
    not POSTGRES_DRIVER_AVAILABLE,
    reason="PostgreSQL driver is required for integration tests",
)
def test_closed_stage_does_not_create_follow_up(client, db_session) -> None:
    organization = Organization(
        name="Closed Automation Org",
        slug=f"closed-automation-{id(db_session)}",
    )
    user = User(
        email=f"closed-automation-{id(db_session)}@example.com",
        full_name="Closed Automation User",
        password_hash=hash_password("Correct Horse Battery Staple"),
    )
    membership = Membership(
        organization=organization,
        user=user,
        role=MembershipRole.OWNER,
    )
    open_stage = PipelineStage(
        organization=organization,
        name="Proposal",
        order_index=30,
        win_probability=0.5,
    )
    closed_stage = PipelineStage(
        organization=organization,
        name="Closed Won",
        order_index=50,
        win_probability=1,
        is_closed=True,
        is_won=True,
    )
    db_session.add_all(
        [organization, user, membership, open_stage, closed_stage],
    )
    db_session.flush()

    opportunity = Opportunity(
        organization=organization,
        owner_user_id=user.id,
        stage=open_stage,
        name="Won Deal",
    )
    db_session.add(opportunity)
    db_session.flush()

    token = create_access_token(user.id)
    response = client.patch(
        f"/api/v1/organizations/{organization.id}/opportunities/{opportunity.id}",
        json={"stage_id": str(closed_stage.id)},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    assert response.json()["status"] == "won"

    assert db_session.scalar(
        select(func.count())
        .select_from(Task)
        .where(Task.opportunity_id == opportunity.id)
    ) == 0
