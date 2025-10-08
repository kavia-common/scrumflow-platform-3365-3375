from __future__ import annotations

from typing import List, Optional
from datetime import datetime

from sqlmodel import Session, select

from .models import (
    Board,
    BoardCreate,
    BoardUpdate,
    Sprint,
    SprintCreate,
    SprintUpdate,
    Task,
    TaskCreate,
    TaskUpdate,
    TeamMember,
    TeamMemberCreate,
    TeamMemberUpdate,
    TaskStatus,
)


# Boards
class BoardRepository:
    def __init__(self, session: Session):
        self.session = session

    # PUBLIC_INTERFACE
    def list(self) -> List[Board]:
        """Return all boards."""
        return self.session.exec(select(Board)).all()

    # PUBLIC_INTERFACE
    def get(self, board_id: int) -> Optional[Board]:
        """Return a board by id."""
        return self.session.get(Board, board_id)

    # PUBLIC_INTERFACE
    def create(self, data: BoardCreate) -> Board:
        """Create a new board."""
        board = Board(**data.model_dump())
        self.session.add(board)
        self.session.commit()
        self.session.refresh(board)
        return board

    # PUBLIC_INTERFACE
    def update(self, board_id: int, data: BoardUpdate) -> Optional[Board]:
        """Update a board."""
        board = self.get(board_id)
        if not board:
            return None
        for k, v in data.model_dump(exclude_unset=True).items():
            setattr(board, k, v)
        self.session.add(board)
        self.session.commit()
        self.session.refresh(board)
        return board

    # PUBLIC_INTERFACE
    def delete(self, board_id: int) -> bool:
        """Delete a board."""
        board = self.get(board_id)
        if not board:
            return False
        self.session.delete(board)
        self.session.commit()
        return True


# Sprints
class SprintRepository:
    def __init__(self, session: Session):
        self.session = session

    # PUBLIC_INTERFACE
    def list(self, board_id: Optional[int] = None) -> List[Sprint]:
        """List sprints optionally filtered by board."""
        query = select(Sprint)
        if board_id is not None:
            query = query.where(Sprint.board_id == board_id)
        return self.session.exec(query).all()

    # PUBLIC_INTERFACE
    def get(self, sprint_id: int) -> Optional[Sprint]:
        """Get a sprint by id."""
        return self.session.get(Sprint, sprint_id)

    # PUBLIC_INTERFACE
    def create(self, data: SprintCreate) -> Sprint:
        """Create a sprint."""
        s = Sprint(**data.model_dump())
        self.session.add(s)
        self.session.commit()
        self.session.refresh(s)
        return s

    # PUBLIC_INTERFACE
    def update(self, sprint_id: int, data: SprintUpdate) -> Optional[Sprint]:
        """Update a sprint."""
        s = self.get(sprint_id)
        if not s:
            return None
        for k, v in data.model_dump(exclude_unset=True).items():
            setattr(s, k, v)
        self.session.add(s)
        self.session.commit()
        self.session.refresh(s)
        return s

    # PUBLIC_INTERFACE
    def delete(self, sprint_id: int) -> bool:
        """Delete a sprint."""
        s = self.get(sprint_id)
        if not s:
            return False
        self.session.delete(s)
        self.session.commit()
        return True


# Tasks
class TaskRepository:
    def __init__(self, session: Session):
        self.session = session

    # PUBLIC_INTERFACE
    def list(
        self,
        board_id: Optional[int] = None,
        sprint_id: Optional[int] = None,
        status: Optional[TaskStatus] = None,
    ) -> List[Task]:
        """List tasks with optional filtering by board, sprint, and status."""
        query = select(Task)
        if board_id is not None:
            query = query.where(Task.board_id == board_id)
        if sprint_id is not None:
            query = query.where(Task.sprint_id == sprint_id)
        if status is not None:
            query = query.where(Task.status == status)
        return self.session.exec(query).all()

    # PUBLIC_INTERFACE
    def get(self, task_id: int) -> Optional[Task]:
        """Get task by id."""
        return self.session.get(Task, task_id)

    # PUBLIC_INTERFACE
    def create(self, data: TaskCreate) -> Task:
        """Create task."""
        t = Task(**data.model_dump())
        self.session.add(t)
        self.session.commit()
        self.session.refresh(t)
        return t

    # PUBLIC_INTERFACE
    def update(self, task_id: int, data: TaskUpdate) -> Optional[Task]:
        """Update task and touch updated_at."""
        t = self.get(task_id)
        if not t:
            return None
        for k, v in data.model_dump(exclude_unset=True).items():
            setattr(t, k, v)
        t.updated_at = datetime.utcnow()
        self.session.add(t)
        self.session.commit()
        self.session.refresh(t)
        return t

    # PUBLIC_INTERFACE
    def delete(self, task_id: int) -> bool:
        """Delete task."""
        t = self.get(task_id)
        if not t:
            return False
        self.session.delete(t)
        self.session.commit()
        return True

    # PUBLIC_INTERFACE
    def move(self, task_id: int, *, sprint_id: Optional[int], board_id: Optional[int], status: Optional[TaskStatus]) -> Optional[Task]:
        """Move task across sprint/board/status."""
        t = self.get(task_id)
        if not t:
            return None
        if sprint_id is not None:
            t.sprint_id = sprint_id
        if board_id is not None:
            t.board_id = board_id
        if status is not None:
            t.status = status
        t.updated_at = datetime.utcnow()
        self.session.add(t)
        self.session.commit()
        self.session.refresh(t)
        return t


# Team
class TeamRepository:
    def __init__(self, session: Session):
        self.session = session

    # PUBLIC_INTERFACE
    def list(self) -> List[TeamMember]:
        """List team members."""
        return self.session.exec(select(TeamMember)).all()

    # PUBLIC_INTERFACE
    def get(self, member_id: int) -> Optional[TeamMember]:
        """Get member by id."""
        return self.session.get(TeamMember, member_id)

    # PUBLIC_INTERFACE
    def create(self, data: TeamMemberCreate) -> TeamMember:
        """Create team member."""
        m = TeamMember(**data.model_dump())
        self.session.add(m)
        self.session.commit()
        self.session.refresh(m)
        return m

    # PUBLIC_INTERFACE
    def update(self, member_id: int, data: TeamMemberUpdate) -> Optional[TeamMember]:
        """Update team member."""
        m = self.get(member_id)
        if not m:
            return None
        for k, v in data.model_dump(exclude_unset=True).items():
            setattr(m, k, v)
        self.session.add(m)
        self.session.commit()
        self.session.refresh(m)
        return m

    # PUBLIC_INTERFACE
    def delete(self, member_id: int) -> bool:
        """Delete team member."""
        m = self.get(member_id)
        if not m:
            return False
        self.session.delete(m)
        self.session.commit()
        return True
