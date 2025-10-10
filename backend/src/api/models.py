from __future__ import annotations

import enum
from datetime import datetime, date
from typing import Optional

from sqlmodel import Field, SQLModel
from sqlalchemy.orm import relationship as sa_relationship

# Note: TYPE_CHECKING block intentionally omitted as we avoid explicit type annotations
# on relationship attributes to prevent SQLAlchemy from attempting to resolve generics like list['Task'].


class TaskStatus(str, enum.Enum):
    todo = "todo"
    in_progress = "in_progress"
    done = "done"
    blocked = "blocked"


class TaskPriority(str, enum.Enum):
    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"


class TeamMemberBase(SQLModel):
    name: str = Field(..., description="Name of the team member")
    role: str = Field(..., description="Role of the team member")


class TeamMember(TeamMemberBase, table=True):
    # Explicit __tablename__ ensures FK naming consistency across SQLAlchemy 2.x
    __tablename__ = "teammember"

    id: Optional[int] = Field(default=None, primary_key=True)
    # Avoid generic-string annotations like list["Task"] which SQLAlchemy attempts to resolve as a class name.
    # Use an untyped attribute assignment with sqlalchemy.orm.relationship to let SA configure properly.
    # Note: keep attribute for runtime only; type checkers can infer via TYPE_CHECKING alias _Task.
    tasks = sa_relationship("Task", back_populates="assignee")


class TeamMemberCreate(TeamMemberBase):
    pass


class TeamMemberRead(TeamMemberBase):
    id: int


class TeamMemberUpdate(SQLModel):
    name: Optional[str] = None
    role: Optional[str] = None


class BoardBase(SQLModel):
    name: str = Field(..., description="Board name")


class Board(BoardBase, table=True):
    __tablename__ = "board"

    id: Optional[int] = Field(default=None, primary_key=True)
    sprints = sa_relationship("Sprint", back_populates="board")
    tasks = sa_relationship("Task", back_populates="board")


class BoardCreate(BoardBase):
    pass


class BoardRead(BoardBase):
    id: int


class BoardUpdate(SQLModel):
    name: Optional[str] = None


class SprintBase(SQLModel):
    name: str = Field(..., description="Sprint name")
    start_date: date = Field(..., description="Sprint start date")
    end_date: date = Field(..., description="Sprint end date")
    goal: Optional[str] = Field(default=None, description="Sprint goal")


class Sprint(SprintBase, table=True):
    __tablename__ = "sprint"

    id: Optional[int] = Field(default=None, primary_key=True)
    board_id: int = Field(foreign_key="board.id", index=True)
    board = sa_relationship("Board", back_populates="sprints")
    tasks = sa_relationship("Task", back_populates="sprint")


class SprintCreate(SprintBase):
    board_id: int


class SprintRead(SprintBase):
    id: int
    board_id: int


class SprintUpdate(SQLModel):
    name: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    goal: Optional[str] = None
    board_id: Optional[int] = None


class TaskBase(SQLModel):
    title: str = Field(..., description="Task title")
    description: Optional[str] = Field(default=None, description="Task description")
    status: TaskStatus = Field(default=TaskStatus.todo, description="Task status")
    priority: TaskPriority = Field(default=TaskPriority.medium, description="Task priority")
    story_points: Optional[int] = Field(default=None, description="Estimated story points")


class Task(TaskBase, table=True):
    __tablename__ = "task"

    id: Optional[int] = Field(default=None, primary_key=True)
    assignee_id: Optional[int] = Field(default=None, foreign_key="teammember.id", index=True)
    sprint_id: Optional[int] = Field(default=None, foreign_key="sprint.id", index=True)
    board_id: int = Field(foreign_key="board.id", index=True)
    # Optional linkage to a Jira issue key (e.g., PROJ-123). Nullable for backward compatibility.
    jira_issue_key: Optional[str] = Field(default=None, description="Linked Jira issue key")

    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    assignee = sa_relationship("TeamMember", back_populates="tasks")
    sprint = sa_relationship("Sprint", back_populates="tasks")
    board = sa_relationship("Board", back_populates="tasks")


class TaskCreate(TaskBase):
    board_id: int
    sprint_id: Optional[int] = None
    assignee_id: Optional[int] = None


class TaskRead(TaskBase):
    id: int
    board_id: int
    sprint_id: Optional[int] = None
    assignee_id: Optional[int] = None
    jira_issue_key: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class TaskUpdate(SQLModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[TaskStatus] = None
    priority: Optional[TaskPriority] = None
    story_points: Optional[int] = None
    assignee_id: Optional[int] = None
    sprint_id: Optional[int] = None
    board_id: Optional[int] = None
    jira_issue_key: Optional[str] = None


# Utility for updated_at timestamps via SQLModel events would be SQLAlchemy-level;
# we'll manually set updated_at in repository updates.
