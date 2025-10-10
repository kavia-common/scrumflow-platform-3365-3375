from typing import Optional

from sqlmodel import Session

from src.core.security import verify_password, create_access_token
from src.db.models import User
from src.db.repositories import get_user_by_email


# PUBLIC_INTERFACE
def authenticate_user(session: Session, email: str, password: str) -> Optional[User]:
    """Authenticate a user by email and password."""
    user = get_user_by_email(session, email)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


# PUBLIC_INTERFACE
def issue_token_for_user(user: User) -> str:
    """Create an access token for a given user."""
    return create_access_token(subject=str(user.id), extra_claims={"email": user.email})
