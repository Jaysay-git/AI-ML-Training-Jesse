from getpass import getpass

from sqlalchemy import select
from app.database.connection import SessionLocal
from app.database.models import User
from app.core.security import hash_password
from email_validator import validate_email, EmailNotValidError


def create_admin():
    email = input("Admin email: ").strip().lower()

    try:
        email = validate_email(email, check_deliverability=False).normalized
    except EmailNotValidError:
        print("Invalid email address.")
        return

    password = getpass("Admin password (minimum 8 characters): ")

    if len(password) < 8:
        print("Password must contain at least 8 characters.")
        return

    confirm_password = getpass("Confirm admin password: ")

    if password != confirm_password:
        print("Passwords do not match.")
        return

    db = SessionLocal()

    try:
        existing_user = db.scalar(
            select(User).where(User.email == email)
        )

        if existing_user:
            print("An account with this email already exists.")
            print("No changes were made.")
            return

        admin = User(
            email=email,
            password_hash=hash_password(password),
            role="admin",
        )

        db.add(admin)
        db.commit()

        print("\nAdministrator account created successfully.")
        print(f"Email: {email}")
        print("Role: admin")

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    create_admin()
