from app.db.base import Base
from app.models import Membership, MembershipRole, Organization, User


def test_identity_tables_are_registered() -> None:
    assert set(Base.metadata.tables) == {
        "organizations",
        "users",
        "organization_memberships",
    }


def test_membership_role_values_are_stable() -> None:
    assert [role.value for role in MembershipRole] == ["owner", "admin", "member"]


def test_identity_constraints_exist() -> None:
    users = Base.metadata.tables[User.__tablename__]
    organizations = Base.metadata.tables[Organization.__tablename__]
    memberships = Base.metadata.tables[Membership.__tablename__]

    assert any(index.unique for index in users.indexes)
    assert any(constraint.name == "uq_membership_org_user" for constraint in memberships.constraints)
    assert any(
        "slug" in [column.name for column in constraint.columns]
        for constraint in organizations.constraints
        if constraint.__class__.__name__ == "UniqueConstraint"
    )
    assert any(index.name == "ix_memberships_org_role" for index in memberships.indexes)
