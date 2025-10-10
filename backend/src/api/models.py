from __future__ import annotations

import enum
from datetime import datetime, date
from typing import Optional, List

from sqlmodel import Field, SQLModel, Relationship


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
    __tablename__ = "teammember"

    id: Optional[int] = Field(default=None, primary_key=True)
    # SQLModel Relationship (list of tasks assigned to this member)
    tasks: List["Task"] = Relationship(
        back_populates="assignee",
        sa_relationship_kwargs={
            "cascade": "all, delete-orphan",
            "foreign_keys": "[Task.assignee_id]",
        },
    )


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
    """Project board model containing sprints and tasks."""
    __tablename__ = "board"

    id: Optional[int] = Field(default=None, primary_key=True)
    sprints: List["Sprint"] = Relationship(
        back_populates="board",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )
    tasks: List["Task"] = Relationship(
        back_populates="board",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )


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
    """Sprint model associated to a board and containing tasks."""
    __tablename__ = "sprint"

    id: Optional[int] = Field(default=None, primary_key=True)
    board_id: int = Field(foreign_key="board.id", index=True)

    board: "Board" = Relationship(
        back_populates="sprints",
        sa_relationship_kwargs={
            "foreign_keys": "[Sprint.board_id]",
        },
    )
    tasks: List["Task"] = Relationship(
        back_populates="sprint",
        sa_relationship_kwargs={
            "cascade": "all, delete-orphan",
            "foreign_keys": "[Task.sprint_id]",
        },
    )


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
    """Task model which may reference a board, sprint, assignee, and optional Jira issue key."""
    __tablename__ = "task"

    id: Optional[int] = Field(default=None, primary_key=True)
    assignee_id: Optional[int] = Field(default=None, foreign_key="teammember.id", index=True)
    sprint_id: Optional[int] = Field(default=None, foreign_key="sprint.id", index=True)
    board_id: int = Field(foreign_key="board.id", index=True)
    jira_issue_key: Optional[str] = Field(default=None, description="Linked Jira issue key")

    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    assignee: Optional["TeamMember"] = Relationship(
        back_populates="tasks",
        sa_relationship_kwargs={
            "foreign_keys": "[Task.assignee_id]",
        },
    )
    sprint: Optional["Sprint"] = Relationship(
        back_populates="tasks",
        sa_relationship_kwargs={
            "foreign_keys": "[Task.sprint_id]",
        },
    )
    board: "Board" = Relationship(
        back_populates="tasks",
        sa_relationship_kwargs={
            "foreign_keys": "[Task.board_id]",
        },
    )


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


# Note: We manually touch updated_at in repositories on write operations.
