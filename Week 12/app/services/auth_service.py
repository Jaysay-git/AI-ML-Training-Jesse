from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.models import User
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
)


def register_user(db: Session, email: str, password: str):
    existing_user = db.scalar(
        select(User).where(User.email == email)
    )

    if existing_user:
        return None

    new_user = User(
        email=email,
        password_hash=hash_password(password),
        role="user",
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


def authenticate_user(db: Session, email: str, password: str):
    user = db.scalar(
        select(User).where(User.email == email)
    )

    if not user:
        return None

    if not verify_password(password, user.password_hash):
        return None

    return user


def create_user_token(user: User):
    return create_access_token({
        "sub": str(user.id),
        "email": user.email,
        "role": user.role,
    })
