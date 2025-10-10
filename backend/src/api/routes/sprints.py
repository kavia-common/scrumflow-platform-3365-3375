from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import Session

from src.api.deps import get_db, get_current_user
from src.db.schemas import SprintCreate, SprintRead
from src.db.repositories import create_sprint, get_board, get_sprint, list_sprints_by_board
from src.db.models import User

router = APIRouter(prefix="/api/sprints", tags=["Boards"])


@router.post("", response_model=SprintRead, status_code=status.HTTP_201_CREATED, summary="Create sprint")
def create_sprint_endpoint(
    payload: SprintCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> SprintRead:
    """Create a sprint on a board. Ensures board exists."""
    board = get_board(db, payload.board_id)
    if not board:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Board not found")
    sprint = create_sprint(db, board_id=payload.board_id, name=payload.name, goal=payload.goal)
    return SprintRead(id=sprint.id, name=sprint.name, goal=sprint.goal, start_date=sprint.start_date, end_date=sprint.end_date, board_id=sprint.board_id, created_at=sprint.created_at)


@router.get("/board/{board_id}", response_model=List[SprintRead], summary="List sprints by board")
def list_sprints_endpoint(
    board_id: int,
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> List[SprintRead]:
    """List sprints for a board."""
    board = get_board(db, board_id)
    if not board:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Board not found")
    sprints = list_sprints_by_board(db, board_id=board_id, limit=limit, offset=offset)
    return [
        SprintRead(
            id=s.id,
            name=s.name,
            goal=s.goal,
            start_date=s.start_date,
            end_date=s.end_date,
            board_id=s.board_id,
            created_at=s.created_at,
        ) for s in sprints
    ]


@router.get("/{sprint_id}", response_model=SprintRead, summary="Get sprint by id")
def get_sprint_endpoint(
    sprint_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> SprintRead:
    """Get sprint by id."""
    sprint = get_sprint(db, sprint_id)
    if not sprint:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sprint not found")
    return SprintRead(
        id=sprint.id,
        name=sprint.name,
        goal=sprint.goal,
        start_date=sprint.start_date,
        end_date=sprint.end_date,
        board_id=sprint.board_id,
        created_at=sprint.created_at,
    )
