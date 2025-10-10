from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlmodel import Session, select

from ..dependencies import get_session
from ..schemas import ProgressSummary
from ..models import Task, TaskStatus

router = APIRouter(prefix="/progress", tags=["Progress"])


@router.get(
    "/summary",
    response_model=ProgressSummary,
    summary="Progress summary",
    description=(
        "Return aggregate counts of tasks by status and a velocity proxy "
        "(sum of story points for done tasks). Allows optional filtering by "
        "board_id or sprint_id."
    ),
)
def progress_summary(
    board_id: Optional[int] = Query(default=None, description="Filter tasks by board"),
    sprint_id: Optional[int] = Query(default=None, description="Filter tasks by sprint"),
    session: Session = Depends(get_session),
):
    query = select(Task)
    if board_id is not None:
        query = query.where(Task.board_id == board_id)
    if sprint_id is not None:
        query = query.where(Task.sprint_id == sprint_id)
    tasks = session.exec(query).all()

    total = len(tasks)
    counts = {
        TaskStatus.todo: 0,
        TaskStatus.in_progress: 0,
        TaskStatus.done: 0,
        TaskStatus.blocked: 0,
    }
    velocity = 0
    for t in tasks:
        counts[t.status] = counts.get(t.status, 0) + 1
        if t.status == TaskStatus.done and t.story_points:
            velocity += int(t.story_points)

    return ProgressSummary(
        total_tasks=total,
        todo=counts[TaskStatus.todo],
        in_progress=counts[TaskStatus.in_progress],
        done=counts[TaskStatus.done],
        blocked=counts[TaskStatus.blocked],
        velocity=velocity,
    )
