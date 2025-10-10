from __future__ import annotations

from typing import Optional
from pydantic import BaseModel, Field

from .models import (
    BoardRead,
    BoardCreate,
    BoardUpdate,
    SprintRead,
    SprintCreate,
    SprintUpdate,
    TaskRead,
    TaskCreate,
    TaskUpdate,
    TeamMemberRead,
    TeamMemberCreate,
    TeamMemberUpdate,
    TaskStatus,
    TaskPriority,
)


# PUBLIC_INTERFACE
class ProgressSummary(BaseModel):
    """Aggregate counts for progress overview."""
    total_tasks: int = Field(..., description="Total number of tasks")
    todo: int = Field(..., description="Tasks in TODO")
    in_progress: int = Field(..., description="Tasks in progress")
    done: int = Field(..., description="Tasks done")
    blocked: int = Field(..., description="Tasks blocked")
    velocity: Optional[int] = Field(
        None,
        description="Sum of story points of 'done' tasks (proxy velocity)",
    )


# Re-export of main models' Pydantic models for API reference
BoardReadModel = BoardRead
BoardCreateModel = BoardCreate
BoardUpdateModel = BoardUpdate

SprintReadModel = SprintRead
SprintCreateModel = SprintCreate
SprintUpdateModel = SprintUpdate

TaskReadModel = TaskRead
TaskCreateModel = TaskCreate
TaskUpdateModel = TaskUpdate

TeamMemberReadModel = TeamMemberRead
TeamMemberCreateModel = TeamMemberCreate
TeamMemberUpdateModel = TeamMemberUpdate

TaskStatusEnum = TaskStatus
TaskPriorityEnum = TaskPriority
