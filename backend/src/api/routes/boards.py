from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import Session

from src.api.deps import get_db, get_current_user
from src.db.schemas import BoardCreate, BoardRead
from src.db.repositories import create_board, get_board, list_boards_by_team, get_team
from src.db.models import User

router = APIRouter(prefix="/api/boards", tags=["Boards"])


@router.post("", response_model=BoardRead, status_code=status.HTTP_201_CREATED, summary="Create board")
def create_board_endpoint(
    payload: BoardCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> BoardRead:
    """Create a board under a team. Ensures team exists."""
    team = get_team(db, payload.team_id)
    if not team:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Team not found")
    # Ownership check (owner of team only)
    if team.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to create board for this team")
    board = create_board(db, team_id=payload.team_id, name=payload.name, description=payload.description)
    return BoardRead(id=board.id, name=board.name, description=board.description, team_id=board.team_id, created_at=board.created_at)


@router.get("/team/{team_id}", response_model=List[BoardRead], summary="List boards by team")
def list_team_boards(
    team_id: int,
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> List[BoardRead]:
    """List boards under a specific team."""
    team = get_team(db, team_id)
    if not team:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Team not found")
    boards = list_boards_by_team(db, team_id=team_id, limit=limit, offset=offset)
    return [BoardRead(id=b.id, name=b.name, description=b.description, team_id=b.team_id, created_at=b.created_at) for b in boards]


@router.get("/{board_id}", response_model=BoardRead, summary="Get board by id")
def get_board_endpoint(
    board_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> BoardRead:
    """Get a board by id."""
    board = get_board(db, board_id)
    if not board:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Board not found")
    return BoardRead(id=board.id, name=board.name, description=board.description, team_id=board.team_id, created_at=board.created_at)
