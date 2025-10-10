from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, Field
from sqlmodel import Session

from src.api.deps import get_db, get_current_user
from src.db.schemas import UserCreate, UserRead
from src.db.repositories import create_user, get_user_by_email
from src.services.auth_service import authenticate_user, issue_token_for_user
from src.db.models import User

router = APIRouter(prefix="/api/auth", tags=["Auth"])


class TokenResponse(BaseModel):
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Token type")


@router.post(
    "/register",
    response_model=UserRead,
    summary="Register user",
    description="Create a new user account."
)
def register_user(payload: UserCreate, db: Session = Depends(get_db)) -> UserRead:
    """Create a new user and return its public info."""
    existing = get_user_by_email(db, payload.email)
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    user = create_user(db, email=payload.email, password=payload.password, full_name=payload.full_name, is_active=True)
    return UserRead(id=user.id, email=user.email, full_name=user.full_name, is_active=user.is_active, created_at=user.created_at)


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Login",
    description="Authenticate with email and password to receive a JWT."
)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)) -> TokenResponse:
    """Authenticate and return a JWT token."""
    # OAuth2PasswordRequestForm uses username field for email by convention
    user = authenticate_user(db, email=form_data.username, password=form_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect email or password")
    token = issue_token_for_user(user)
    return TokenResponse(access_token=token)


@router.get(
    "/me",
    response_model=UserRead,
    summary="Current user",
    description="Get information about the current authenticated user."
)
def read_me(current_user: User = Depends(get_current_user)) -> UserRead:
    """Return the current authenticated user's profile."""
    return UserRead(
        id=current_user.id,
        email=current_user.email,
        full_name=current_user.full_name,
        is_active=current_user.is_active,
        created_at=current_user.created_at,
    )
