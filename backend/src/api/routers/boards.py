from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from ..dependencies import get_session
from ..models import BoardCreate, BoardRead, BoardUpdate
from ..repositories import BoardRepository

router = APIRouter(prefix="/boards", tags=["Boards"])


@router.get(
    "",
    response_model=list[BoardRead],
    summary="List boards",
    description="Retrieve all boards.",
)
def list_boards(session: Session = Depends(get_session)):
    repo = BoardRepository(session)
    return repo.list()


@router.post(
    "",
    response_model=BoardRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create board",
    description="Create a new board.",
)
def create_board(payload: BoardCreate, session: Session = Depends(get_session)):
    repo = BoardRepository(session)
    return repo.create(payload)


@router.get(
    "/{board_id}",
    response_model=BoardRead,
    summary="Get board",
    description="Get a board by id.",
)
def get_board(board_id: int, session: Session = Depends(get_session)):
    repo = BoardRepository(session)
    b = repo.get(board_id)
    if not b:
        raise HTTPException(status_code=404, detail="Board not found")
    return b


@router.put(
    "/{board_id}",
    response_model=BoardRead,
    summary="Update board",
    description="Update a board by id.",
)
def update_board(board_id: int, payload: BoardUpdate, session: Session = Depends(get_session)):
    repo = BoardRepository(session)
    b = repo.update(board_id, payload)
    if not b:
        raise HTTPException(status_code=404, detail="Board not found")
    return b


@router.delete(
    "/{board_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete board",
    description="Delete a board by id.",
)
def delete_board(board_id: int, session: Session = Depends(get_session)):
    repo = BoardRepository(session)
    ok = repo.delete(board_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Board not found")
    return None
