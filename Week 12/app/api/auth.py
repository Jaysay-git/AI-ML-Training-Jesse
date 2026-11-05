
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.api.dependencies import get_current_user
from app.database.models import User
from app.schemas.auth import (
    UserCreate,
    UserLogin,
    UserResponse,
    TokenResponse,
)
from app.services.auth_service import (
    register_user,
    authenticate_user,
    create_user_token,
)
from app.core.limiter import limiter

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/signup",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
@limiter.limit("3/hour")
def signup(
    request: Request,
    user_data: UserCreate,
    db: Session = Depends(get_db),
):
    user = register_user(
        db=db,
        email=str(user_data.email).lower(),
        password=user_data.password,
    )

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists",
        )

    return user


@router.post("/login", response_model=TokenResponse)
@limiter.limit("5/minute")
def login(
    request: Request,
    credentials: UserLogin,
    db: Session = Depends(get_db),
):
    user = authenticate_user(
        db=db,
        email=str(credentials.email).lower(),
        password=credentials.password,
    )

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    access_token = create_user_token(user)

    return TokenResponse(access_token=access_token)


@router.get("/me", response_model=UserResponse)
def get_my_account(
    current_user: User = Depends(get_current_user),
):
    return current_user
