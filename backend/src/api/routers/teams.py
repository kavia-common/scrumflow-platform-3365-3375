from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from ..dependencies import get_session
from ..models import TeamMemberCreate, TeamMemberRead, TeamMemberUpdate
from ..repositories import TeamRepository

router = APIRouter(prefix="/team", tags=["Team"])


@router.get(
    "",
    response_model=list[TeamMemberRead],
    summary="List team",
    description="List all team members.",
)
def list_team(session: Session = Depends(get_session)):
    repo = TeamRepository(session)
    return repo.list()


@router.post(
    "",
    response_model=TeamMemberRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create team member",
    description="Create a new team member.",
)
def create_member(payload: TeamMemberCreate, session: Session = Depends(get_session)):
    repo = TeamRepository(session)
    return repo.create(payload)


@router.get(
    "/{member_id}",
    response_model=TeamMemberRead,
    summary="Get team member",
    description="Get a team member by id.",
)
def get_member(member_id: int, session: Session = Depends(get_session)):
    repo = TeamRepository(session)
    m = repo.get(member_id)
    if not m:
        raise HTTPException(status_code=404, detail="Team member not found")
    return m


@router.put(
    "/{member_id}",
    response_model=TeamMemberRead,
    summary="Update team member",
    description="Update a team member by id.",
)
def update_member(member_id: int, payload: TeamMemberUpdate, session: Session = Depends(get_session)):
    repo = TeamRepository(session)
    m = repo.update(member_id, payload)
    if not m:
        raise HTTPException(status_code=404, detail="Team member not found")
    return m


@router.delete(
    "/{member_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete team member",
    description="Delete a team member by id.",
)
def delete_member(member_id: int, session: Session = Depends(get_session)):
    repo = TeamRepository(session)
    ok = repo.delete(member_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Team member not found")
    return None
