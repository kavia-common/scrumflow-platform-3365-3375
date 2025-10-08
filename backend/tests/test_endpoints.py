from typing import Generator

import pytest
from fastapi.testclient import TestClient
from sqlmodel import SQLModel, create_engine, Session

# Import the app and get_session from our API
from src.api.main import app
from src.api.dependencies import get_session
from src.api.models import Board


def make_test_engine():
    """
    Create an in-memory SQLite engine suitable for tests.
    check_same_thread False allows usage across threads for TestClient.
    """
    return create_engine("sqlite://", connect_args={"check_same_thread": False})


@pytest.fixture(name="session")
def session_fixture() -> Generator[Session, None, None]:
    """
    Provide a fresh database session bound to a new in-memory database
    for each test function.
    """
    engine = make_test_engine()
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(session: Session) -> Generator[TestClient, None, None]:
    """
    Provide a TestClient that overrides the get_session dependency to
    use our in-memory session for reliable, isolated tests.
    """

    def override_get_session() -> Generator[Session, None, None]:
        # Yield the existing session within the same scope/transaction.
        yield session

    app.dependency_overrides[get_session] = override_get_session
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


def seed_board(session: Session) -> int:
    """
    Insert a simple board to satisfy foreign key for tasks.
    """
    b = Board(name="Test Board")
    session.add(b)
    session.commit()
    session.refresh(b)
    return b.id


def test_health_check(client: TestClient):
    r = client.get("/")
    assert r.status_code == 200
    data = r.json()
    assert data.get("message") == "Healthy"


def test_create_and_list_tasks(client: TestClient, session: Session):
    board_id = seed_board(session)

    # Create a task
    payload = {
        "title": "Write unit tests",
        "description": "Cover key endpoints",
        "board_id": board_id,
        "status": "todo",
    }
    r = client.post("/tasks", json=payload)
    assert r.status_code == 201, r.text
    created = r.json()
    assert created["title"] == payload["title"]
    assert created["board_id"] == board_id
    assert created["status"] == "todo"
    task_id = created["id"]

    # List tasks (no filter)
    r = client.get("/tasks")
    assert r.status_code == 200
    tasks = r.json()
    assert isinstance(tasks, list)
    assert any(t["id"] == task_id for t in tasks)

    # List tasks filtered by board_id
    r = client.get(f"/tasks?board_id={board_id}")
    assert r.status_code == 200
    tasks = r.json()
    assert len(tasks) >= 1
    assert all(t["board_id"] == board_id for t in tasks)


def test_move_task_and_progress_summary(client: TestClient, session: Session):
    board_id = seed_board(session)

    # Create a couple of tasks with story points to test velocity
    t1 = client.post(
        "/tasks",
        json={
            "title": "Task A",
            "board_id": board_id,
            "status": "todo",
            "story_points": 3,
        },
    ).json()
    client.post(
        "/tasks",
        json={
            "title": "Task B",
            "board_id": board_id,
            "status": "in_progress",
            "story_points": 5,
        },
    ).json()

    # Move t1 to done
    move_payload = {"status": "done"}
    r = client.post(f"/tasks/{t1['id']}/move", json=move_payload)
    assert r.status_code == 200, r.text
    moved = r.json()
    assert moved["status"] == "done"

    # Check progress summary for this board
    r = client.get(f"/progress/summary?board_id={board_id}")
    assert r.status_code == 200
    summary = r.json()

    # Validate keys present
    for key in ["total_tasks", "todo", "in_progress", "done", "blocked", "velocity"]:
        assert key in summary

    assert summary["total_tasks"] == 2
    assert summary["done"] == 1
    assert summary["todo"] in (0, 1)  # depending on other statuses
    assert summary["in_progress"] in (0, 1)
    # Velocity should be sum of story_points for done tasks (t1=3)
    assert summary["velocity"] == 3
