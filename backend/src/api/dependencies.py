from __future__ import annotations

import os
from typing import Generator
from datetime import date, timedelta

from dotenv import load_dotenv
from sqlmodel import SQLModel, Session, create_engine, select

from .models import (
    Board,
    Sprint,
    Task,
    TeamMember,
    TaskStatus,
    TaskPriority,
)

# Load environment variables
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./scrum_mind.db")
SEED = os.getenv("SEED", "false").lower() in ("1", "true", "yes", "on")

# SQLite specific connection args
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(DATABASE_URL, echo=False, connect_args=connect_args)


# PUBLIC_INTERFACE
def get_session() -> Generator[Session, None, None]:
    """FastAPI dependency that yields a database session and ensures it is closed after use."""
    with Session(engine) as session:
        yield session


def init_db_and_seed() -> None:
    """
    Create all tables and optionally seed initial development data if SEED is enabled.
    """
    SQLModel.metadata.create_all(engine)

    if not SEED:
        return

    with Session(engine) as session:
        # Check if already seeded
        boards_count = session.exec(select(Board)).first()
        if boards_count:
            return

        # Seed data
        board = Board(name="Example Project")
        session.add(board)
        session.commit()
        session.refresh(board)

        tm_alice = TeamMember(name="Alice", role="Developer")
        tm_bob = TeamMember(name="Bob", role="Product Owner")
        session.add(tm_alice)
        session.add(tm_bob)
        session.commit()
        session.refresh(tm_alice)
        session.refresh(tm_bob)

        today = date.today()
        sprint1 = Sprint(
            name="Sprint 1",
            start_date=today - timedelta(days=7),
            end_date=today + timedelta(days=7),
            goal="Deliver MVP",
            board_id=board.id,
        )
        session.add(sprint1)
        session.commit()
        session.refresh(sprint1)

        t1 = Task(
            title="Setup project",
            description="Initialize repository and CI",
            status=TaskStatus.done,
            priority=TaskPriority.medium,
            story_points=3,
            assignee_id=tm_alice.id,
            sprint_id=sprint1.id,
            board_id=board.id,
        )
        t2 = Task(
            title="Design API",
            description="Define endpoints and schemas",
            status=TaskStatus.in_progress,
            priority=TaskPriority.high,
            story_points=5,
            assignee_id=tm_alice.id,
            sprint_id=sprint1.id,
            board_id=board.id,
        )
        t3 = Task(
            title="Write docs",
            description="Create README and API docs",
            status=TaskStatus.todo,
            priority=TaskPriority.low,
            story_points=2,
            assignee_id=tm_bob.id,
            sprint_id=sprint1.id,
            board_id=board.id,
        )
        session.add(t1)
        session.add(t2)
        session.add(t3)
        session.commit()
