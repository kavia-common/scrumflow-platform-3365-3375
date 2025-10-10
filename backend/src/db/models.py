from datetime import datetime
from typing import Optional, List

from sqlmodel import Field, Relationship, SQLModel


class TeamMemberLink(SQLModel, table=True):
    """Association table between users and teams with role."""
    __tablename__ = "team_members"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    team_id: int = Field(foreign_key="teams.id", index=True)
    role: str = Field(default="member", index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class User(SQLModel, table=True):
    """User account model."""
    __tablename__ = "users"

    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(index=True, unique=True)
    hashed_password: str
    full_name: Optional[str] = None
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    teams: List["Team"] = Relationship(
        back_populates="members",
        link_model=TeamMemberLink,
        sa_relationship_kwargs={"lazy": "selectin"},
    )


class Team(SQLModel, table=True):
    """Team model representing a group of users collaborating."""
    __tablename__ = "teams"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    description: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    owner_id: Optional[int] = Field(foreign_key="users.id", index=True)

    owner: Optional[User] = Relationship(sa_relationship_kwargs={"lazy": "selectin"})
    members: List[User] = Relationship(
        back_populates="teams",
        link_model=TeamMemberLink,
        sa_relationship_kwargs={"lazy": "selectin"},
    )

    boards: List["Board"] = Relationship(back_populates="team", sa_relationship_kwargs={"lazy": "selectin"})


class Board(SQLModel, table=True):
    """Board model for organizing sprints and tasks."""
    __tablename__ = "boards"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    description: Optional[str] = None
    team_id: int = Field(foreign_key="teams.id", index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    team: Team = Relationship(back_populates="boards", sa_relationship_kwargs={"lazy": "selectin"})
    sprints: List["Sprint"] = Relationship(back_populates="board", sa_relationship_kwargs={"lazy": "selectin"})


class Sprint(SQLModel, table=True):
    """Sprint model for time-boxed iterations."""
    __tablename__ = "sprints"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    goal: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    board_id: int = Field(foreign_key="boards.id", index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    board: Board = Relationship(back_populates="sprints", sa_relationship_kwargs={"lazy": "selectin"})
    tasks: List["Task"] = Relationship(back_populates="sprint", sa_relationship_kwargs={"lazy": "selectin"})


class Task(SQLModel, table=True):
    """Task model in a sprint or backlog."""
    __tablename__ = "tasks"

    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    description: Optional[str] = None
    status: str = Field(default="todo", index=True)  # todo, in_progress, done
    assignee_id: Optional[int] = Field(default=None, foreign_key="users.id", index=True)
    sprint_id: Optional[int] = Field(default=None, foreign_key="sprints.id", index=True)
    board_id: int = Field(foreign_key="boards.id", index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    sprint: Optional[Sprint] = Relationship(back_populates="tasks", sa_relationship_kwargs={"lazy": "selectin"})
