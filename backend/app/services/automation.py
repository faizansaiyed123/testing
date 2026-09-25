from datetime import UTC, datetime, timedelta
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Opportunity, PipelineStage, Task
from app.services.audit import record_audit


def create_stage_follow_up_task(
    db: Session,
    *,
    opportunity: Opportunity,
    stage: PipelineStage,
    actor_user_id: UUID,
) -> Task | None:
    if stage.is_closed:
        return None

    automation_key = f"stage-follow-up:{opportunity.id}:{stage.id}"
    existing = db.scalar(
        select(Task)
        .where(Task.organization_id == opportunity.organization_id)
        .where(Task.automation_key == automation_key)
        .limit(1)
    )
    if existing is not None:
        return existing

    task = Task(
        organization_id=opportunity.organization_id,
        created_by_user_id=actor_user_id,
        assigned_to_user_id=opportunity.owner_user_id,
        company_id=opportunity.company_id,
        contact_id=opportunity.contact_id,
        opportunity_id=opportunity.id,
        title=f"Follow up on {opportunity.name}",
        description=f"Follow up after moving to the {stage.name} stage.",
        priority="high",
        automation_key=automation_key,
        due_at=datetime.now(UTC) + timedelta(days=2),
    )
    db.add(task)
    db.flush()

    record_audit(
        db,
        organization_id=opportunity.organization_id,
        actor_user_id=actor_user_id,
        entity_type="task",
        entity_id=task.id,
        action="automation_created",
        summary=f"Created follow-up for {opportunity.name} after stage change",
        after_data={
            "automation_key": automation_key,
            "opportunity_id": str(opportunity.id),
            "stage_id": str(stage.id),
            "due_at": task.due_at.isoformat(),
        },
    )
    return task
