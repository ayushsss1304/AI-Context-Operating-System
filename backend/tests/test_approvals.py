from app.api.routes.approvals import review_approval
from app.models.activity import Activity
from app.models.approval import Approval
from app.models.task import Task
from app.models.workspace import Workspace
from sqlmodel import select


def test_review_approval_marks_approval_approved(session):
    workspace = Workspace(name="Approval Test")
    session.add(workspace)
    session.commit()
    session.refresh(workspace)

    task = Task(workspace_id=workspace.id, title="Approve recommendation")
    session.add(task)
    session.commit()
    session.refresh(task)

    approval = Approval(
        workspace_id=workspace.id,
        task_id=task.id,
        title="Final recommendation",
        content="Approve the recommendation.",
    )
    session.add(approval)
    session.commit()
    session.refresh(approval)

    reviewed = review_approval(approval.id, "approved", "Ayush", session)

    assert reviewed.status == "approved"
    assert reviewed.reviewed_by == "Ayush"
    assert reviewed.reviewed_at is not None

    session.refresh(task)
    assert task.status == "approved"

    activities = session.exec(select(Activity).where(Activity.task_id == task.id)).all()
    assert len(activities) == 1
    assert activities[0].action_type == "approval_reviewed"


def test_review_approval_marks_task_rejected(session):
    workspace = Workspace(name="Reject Approval Test")
    session.add(workspace)
    session.commit()
    session.refresh(workspace)

    task = Task(workspace_id=workspace.id, title="Reject recommendation")
    session.add(task)
    session.commit()
    session.refresh(task)

    approval = Approval(
        workspace_id=workspace.id,
        task_id=task.id,
        title="Final recommendation",
        content="Reject the recommendation.",
    )
    session.add(approval)
    session.commit()
    session.refresh(approval)

    reviewed = review_approval(approval.id, "rejected", "Ayush", session)

    assert reviewed.status == "rejected"
    session.refresh(task)
    assert task.status == "rejected"
