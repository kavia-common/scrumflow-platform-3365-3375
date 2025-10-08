from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlmodel import Session

from ..dependencies import get_session
from ..models import TaskCreate, TaskRead, TaskUpdate, TaskStatus
from ..repositories import TaskRepository

router = APIRouter(prefix="/tasks", tags=["Tasks"])


@router.get(
    "",
    response_model=list[TaskRead],
    summary="List tasks",
    description="List tasks optionally filtered by board_id, sprint_id, and status.",
)
def list_tasks(
    board_id: Optional[int] = Query(default=None, description="Filter by board id"),
    sprint_id: Optional[int] = Query(default=None, description="Filter by sprint id"),
    status: Optional[TaskStatus] = Query(default=None, description="Filter by status"),
    session: Session = Depends(get_session),
):
    repo = TaskRepository(session)
    return repo.list(board_id=board_id, sprint_id=sprint_id, status=status)


@router.post(
    "",
    response_model=TaskRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create task",
    description="Create a new task.",
)
def create_task(payload: TaskCreate, session: Session = Depends(get_session)):
    repo = TaskRepository(session)
    return repo.create(payload)


@router.get(
    "/{task_id}",
    response_model=TaskRead,
    summary="Get task",
    description="Get a task by id.",
)
def get_task(task_id: int, session: Session = Depends(get_session)):
    repo = TaskRepository(session)
    t = repo.get(task_id)
    if not t:
        raise HTTPException(status_code=404, detail="Task not found")
    return t


@router.put(
    "/{task_id}",
    response_model=TaskRead,
    summary="Update task",
    description="Update a task by id.",
)
def update_task(task_id: int, payload: TaskUpdate, session: Session = Depends(get_session)):
    repo = TaskRepository(session)
    t = repo.update(task_id, payload)
    if not t:
        raise HTTPException(status_code=404, detail="Task not found")
    return t


@router.delete(
    "/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete task",
    description="Delete a task by id.",
)
def delete_task(task_id: int, session: Session = Depends(get_session)):
    repo = TaskRepository(session)
    ok = repo.delete(task_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Task not found")
    return None


class MoveTaskPayload(BaseModel):
    sprint_id: Optional[int] = Field(default=None, description="New sprint id")
    board_id: Optional[int] = Field(default=None, description="New board id")
    status: Optional[TaskStatus] = Field(default=None, description="New status")


@router.post(
    "/{task_id}/move",
    response_model=TaskRead,
    summary="Move task",
    description="Move task across sprint/board/status in a single operation.",
)
def move_task(task_id: int, payload: MoveTaskPayload, session: Session = Depends(get_session)):
    repo = TaskRepository(session)
    t = repo.move(task_id, sprint_id=payload.sprint_id, board_id=payload.board_id, status=payload.status)
    if not t:
        raise HTTPException(status_code=404, detail="Task not found")
    return t
