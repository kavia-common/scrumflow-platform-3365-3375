from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


# User Schemas
class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None
    is_active: bool = True


class UserCreate(UserBase):
    password: str = Field(min_length=6)


class UserRead(UserBase):
    id: int
    created_at: datetime


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    is_active: Optional[bool] = None
    password: Optional[str] = Field(default=None, min_length=6)


# Team Schemas
class TeamBase(BaseModel):
    name: str
    description: Optional[str] = None


class TeamCreate(TeamBase):
    owner_id: Optional[int] = None


class TeamRead(TeamBase):
    id: int
    owner_id: Optional[int]
    created_at: datetime


class TeamUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None


# Board Schemas
class BoardBase(BaseModel):
    name: str
    description: Optional[str] = None


class BoardCreate(BoardBase):
    team_id: int


class BoardRead(BoardBase):
    id: int
    team_id: int
    created_at: datetime


class BoardUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None


# Sprint Schemas
class SprintBase(BaseModel):
    name: str
    goal: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None


class SprintCreate(SprintBase):
    board_id: int


class SprintRead(SprintBase):
    id: int
    board_id: int
    created_at: datetime


class SprintUpdate(BaseModel):
    name: Optional[str] = None
    goal: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None


# Task Schemas
class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    status: str = "todo"
    assignee_id: Optional[int] = None


class TaskCreate(TaskBase):
    board_id: int
    sprint_id: Optional[int] = None


class TaskRead(TaskBase):
    id: int
    board_id: int
    sprint_id: Optional[int]
    created_at: datetime


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    assignee_id: Optional[int] = None
    board_id: Optional[int] = None
    sprint_id: Optional[int] = None
