from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import Session

from src.api.deps import get_db, get_current_user
from src.db.schemas import TeamCreate, TeamRead
from src.db.repositories import create_team, get_team, list_teams
from src.db.models import User

router = APIRouter(prefix="/api/teams", tags=["Teams"])


@router.post("", response_model=TeamRead, status_code=status.HTTP_201_CREATED, summary="Create team")
def create_team_endpoint(
    payload: TeamCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> TeamRead:
    """Create a team owned by the current user unless owner_id specified and same as current user."""
    owner_id = payload.owner_id if payload.owner_id is not None else current_user.id
    if owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cannot create team for another owner")
    team = create_team(db, name=payload.name, description=payload.description, owner_id=owner_id)
    return TeamRead(id=team.id, name=team.name, description=team.description, owner_id=team.owner_id, created_at=team.created_at)


@router.get("", response_model=List[TeamRead], summary="List teams")
def list_teams_endpoint(
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> List[TeamRead]:
    """List teams (simple global list for now)."""
    teams = list_teams(db, limit=limit, offset=offset)
    return [TeamRead(id=t.id, name=t.name, description=t.description, owner_id=t.owner_id, created_at=t.created_at) for t in teams]


@router.get("/{team_id}", response_model=TeamRead, summary="Get team by id")
def get_team_endpoint(
    team_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> TeamRead:
    """Get a team by id."""
    team = get_team(db, team_id)
    if not team:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Team not found")
    return TeamRead(id=team.id, name=team.name, description=team.description, owner_id=team.owner_id, created_at=team.created_at)
