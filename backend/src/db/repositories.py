from typing import List, Optional, Type, TypeVar

from sqlmodel import Session, select

from src.db.models import Board, Sprint, Task, Team, User
from src.core.security import hash_password

ModelT = TypeVar("ModelT", User, Team, Board, Sprint, Task)


def _get_or_none(session: Session, model: Type[ModelT], obj_id: int) -> Optional[ModelT]:
    return session.get(model, obj_id)


# PUBLIC_INTERFACE
def create_user(session: Session, email: str, password: str, full_name: Optional[str] = None, is_active: bool = True) -> User:
    """Create a new user with hashed password."""
    user = User(email=email, hashed_password=hash_password(password), full_name=full_name, is_active=is_active)
    session.add(user)
    session.flush()
    return user


# PUBLIC_INTERFACE
def get_user_by_email(session: Session, email: str) -> Optional[User]:
    """Get user by email."""
    return session.exec(select(User).where(User.email == email)).first()


# PUBLIC_INTERFACE
def get_user(session: Session, user_id: int) -> Optional[User]:
    """Get user by id."""
    return _get_or_none(session, User, user_id)


# PUBLIC_INTERFACE
def list_users(session: Session, limit: int = 100, offset: int = 0) -> List[User]:
    """List users with pagination."""
    return list(session.exec(select(User).offset(offset).limit(limit)))


# PUBLIC_INTERFACE
def update_user_password(session: Session, user_id: int, new_password: str) -> Optional[User]:
    """Update a user's password."""
    user = _get_or_none(session, User, user_id)
    if not user:
        return None
    user.hashed_password = hash_password(new_password)
    session.add(user)
    session.flush()
    return user


# PUBLIC_INTERFACE
def create_team(session: Session, name: str, description: Optional[str] = None, owner_id: Optional[int] = None) -> Team:
    """Create a new team."""
    team = Team(name=name, description=description, owner_id=owner_id)
    session.add(team)
    session.flush()
    return team


# PUBLIC_INTERFACE
def get_team(session: Session, team_id: int) -> Optional[Team]:
    """Get team by id."""
    return _get_or_none(session, Team, team_id)


# PUBLIC_INTERFACE
def list_teams(session: Session, limit: int = 100, offset: int = 0) -> List[Team]:
    """List teams with pagination."""
    return list(session.exec(select(Team).offset(offset).limit(limit)))


# PUBLIC_INTERFACE
def create_board(session: Session, team_id: int, name: str, description: Optional[str] = None) -> Board:
    """Create a new board for a team."""
    board = Board(team_id=team_id, name=name, description=description)
    session.add(board)
    session.flush()
    return board


# PUBLIC_INTERFACE
def get_board(session: Session, board_id: int) -> Optional[Board]:
    """Get board by id."""
    return _get_or_none(session, Board, board_id)


# PUBLIC_INTERFACE
def list_boards_by_team(session: Session, team_id: int, limit: int = 100, offset: int = 0) -> List[Board]:
    """List boards for a given team."""
    return list(session.exec(select(Board).where(Board.team_id == team_id).offset(offset).limit(limit)))


# PUBLIC_INTERFACE
def create_sprint(session: Session, board_id: int, name: str, goal: Optional[str] = None) -> Sprint:
    """Create a sprint on a board."""
    sprint = Sprint(board_id=board_id, name=name, goal=goal)
    session.add(sprint)
    session.flush()
    return sprint


# PUBLIC_INTERFACE
def get_sprint(session: Session, sprint_id: int) -> Optional[Sprint]:
    """Get sprint by id."""
    return _get_or_none(session, Sprint, sprint_id)


# PUBLIC_INTERFACE
def list_sprints_by_board(session: Session, board_id: int, limit: int = 100, offset: int = 0) -> List[Sprint]:
    """List sprints for a board."""
    return list(session.exec(select(Sprint).where(Sprint.board_id == board_id).offset(offset).limit(limit)))


# PUBLIC_INTERFACE
def create_task(
    session: Session,
    board_id: int,
    title: str,
    description: Optional[str] = None,
    status: str = "todo",
    sprint_id: Optional[int] = None,
    assignee_id: Optional[int] = None,
) -> Task:
    """Create a task."""
    task = Task(
        board_id=board_id,
        title=title,
        description=description,
        status=status,
        sprint_id=sprint_id,
        assignee_id=assignee_id,
    )
    session.add(task)
    session.flush()
    return task


# PUBLIC_INTERFACE
def get_task(session: Session, task_id: int) -> Optional[Task]:
    """Get task by id."""
    return _get_or_none(session, Task, task_id)


# PUBLIC_INTERFACE
def list_tasks_by_board(session: Session, board_id: int, limit: int = 100, offset: int = 0) -> List[Task]:
    """List tasks for a board."""
    return list(session.exec(select(Task).where(Task.board_id == board_id).offset(offset).limit(limit)))


# PUBLIC_INTERFACE
def update_task_status(session: Session, task_id: int, status: str) -> Optional[Task]:
    """Update task status."""
    task = _get_or_none(session, Task, task_id)
    if not task:
        return None
    task.status = status
    session.add(task)
    session.flush()
    return task
