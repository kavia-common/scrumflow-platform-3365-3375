from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlmodel import Session, select

from src.api.deps import get_db, get_current_user
from src.db.schemas import TaskCreate, TaskRead
from src.db.repositories import create_task, get_board, get_task, update_task_status
from src.db.models import User, Task

router = APIRouter(prefix="/api/tasks", tags=["Boards"])


@router.post("", response_model=TaskRead, status_code=status.HTTP_201_CREATED, summary="Create task")
def create_task_endpoint(
    payload: TaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> TaskRead:
    """Create a task on a board (optionally linked to a sprint)."""
    board = get_board(db, payload.board_id)
    if not board:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Board not found")
    task = create_task(
        db,
        board_id=payload.board_id,
        title=payload.title,
        description=payload.description,
        status=payload.status,
        sprint_id=payload.sprint_id,
        assignee_id=payload.assignee_id,
    )
    return TaskRead(
        id=task.id,
        title=task.title,
        description=task.description,
        status=task.status,
        assignee_id=task.assignee_id,
        board_id=task.board_id,
        sprint_id=task.sprint_id,
        created_at=task.created_at,
    )


@router.get("/board/{board_id}", response_model=List[TaskRead], summary="List tasks by board with optional filters")
def list_tasks_endpoint(
    board_id: int,
    status_filter: Optional[str] = Query(default=None, description="Filter by status"),
    assignee_id: Optional[int] = Query(default=None, description="Filter by assignee"),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> List[TaskRead]:
    """List tasks for a board with optional filters."""
    board = get_board(db, board_id)
    if not board:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Board not found")
    # Start from base list
    query = select(Task).where(Task.board_id == board_id)
    if status_filter:
        query = query.where(Task.status == status_filter)
    if assignee_id:
        query = query.where(Task.assignee_id == assignee_id)
    tasks = list(db.exec(query.offset(offset).limit(limit)))
    return [
        TaskRead(
            id=t.id,
            title=t.title,
            description=t.description,
            status=t.status,
            assignee_id=t.assignee_id,
            board_id=t.board_id,
            sprint_id=t.sprint_id,
            created_at=t.created_at,
        ) for t in tasks
    ]


@router.get("/{task_id}", response_model=TaskRead, summary="Get task by id")
def get_task_endpoint(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> TaskRead:
    """Get a task by id."""
    task = get_task(db, task_id)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return TaskRead(
        id=task.id,
        title=task.title,
        description=task.description,
        status=task.status,
        assignee_id=task.assignee_id,
        board_id=task.board_id,
        sprint_id=task.sprint_id,
        created_at=task.created_at,
    )


class StatusUpdate(BaseModel):
    status: str


@router.patch("/{task_id}/status", response_model=TaskRead, summary="Update task status")
def update_task_status_endpoint(
    task_id: int,
    update: StatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> TaskRead:
    """Update the status of a task."""
    task = update_task_status(db, task_id=task_id, status=update.status)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return TaskRead(
        id=task.id,
        title=task.title,
        description=task.description,
        status=task.status,
        assignee_id=task.assignee_id,
        board_id=task.board_id,
        sprint_id=task.sprint_id,
        created_at=task.created_at,
    )
