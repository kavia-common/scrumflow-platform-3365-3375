from contextlib import contextmanager
from typing import Generator

from sqlmodel import Session, SQLModel, create_engine

from src.core.config import get_db_url


_engine = None


def get_engine():
    """Lazy init engine to avoid creating before config is ready."""
    global _engine
    if _engine is None:
        url = get_db_url()
        connect_args = {"check_same_thread": False} if url.startswith("sqlite") else {}
        _engine = create_engine(url, echo=False, future=True, connect_args=connect_args)
    return _engine


# PUBLIC_INTERFACE
def init_db() -> None:
    """Create database tables if they do not exist."""
    engine = get_engine()
    # Import models to register with SQLModel metadata before creating tables
    import src.db.models  # noqa: F401
    SQLModel.metadata.create_all(engine)


# PUBLIC_INTERFACE
@contextmanager
def get_session() -> Generator[Session, None, None]:
    """Provide a transactional SQLModel Session."""
    engine = get_engine()
    session = Session(engine)
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
