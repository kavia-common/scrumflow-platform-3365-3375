from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import Session

from ..dependencies import get_session
from ..models import SprintCreate, SprintRead, SprintUpdate
from ..repositories import SprintRepository

router = APIRouter(prefix="/sprints", tags=["Sprints"])


@router.get(
    "",
    response_model=list[SprintRead],
    summary="List sprints",
    description="List all sprints, optionally filtered by board_id.",
)
def list_sprints(
    board_id: Optional[int] = Query(default=None, description="Filter by board id"),
    session: Session = Depends(get_session),
):
    repo = SprintRepository(session)
    return repo.list(board_id=board_id)


@router.post(
    "",
    response_model=SprintRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create sprint",
    description="Create a new sprint.",
)
def create_sprint(payload: SprintCreate, session: Session = Depends(get_session)):
    repo = SprintRepository(session)
    return repo.create(payload)


@router.get(
    "/{sprint_id}",
    response_model=SprintRead,
    summary="Get sprint",
    description="Get a sprint by id.",
)
def get_sprint(sprint_id: int, session: Session = Depends(get_session)):
    repo = SprintRepository(session)
    s = repo.get(sprint_id)
    if not s:
        raise HTTPException(status_code=404, detail="Sprint not found")
    return s


@router.put(
    "/{sprint_id}",
    response_model=SprintRead,
    summary="Update sprint",
    description="Update a sprint by id.",
)
def update_sprint(sprint_id: int, payload: SprintUpdate, session: Session = Depends(get_session)):
    repo = SprintRepository(session)
    s = repo.update(sprint_id, payload)
    if not s:
        raise HTTPException(status_code=404, detail="Sprint not found")
    return s


@router.delete(
    "/{sprint_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete sprint",
    description="Delete a sprint by id.",
)
def delete_sprint(sprint_id: int, session: Session = Depends(get_session)):
    repo = SprintRepository(session)
    ok = repo.delete(sprint_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Sprint not found")
    return None
