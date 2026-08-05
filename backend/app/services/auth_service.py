from sqlalchemy.orm import Session

from app.auth.hashing import hash_password, verify_password
from app.auth.jwt_handler import create_access_token
from app.models.user import User
from app.repositories.user_repository import user_repository
from app.schemas.user_schema import UserRegister


class AuthService:

    def register_user(
        self,
        db: Session,
        user_data: UserRegister
    ):

        existing_user = user_repository.get_by_email(
            db,
            user_data.email
        )

        if existing_user:
            raise ValueError("Email already registered")

        new_user = User(
            full_name=user_data.full_name,
            email=user_data.email,
            password_hash=hash_password(user_data.password)
        )

        return user_repository.create(
            db,
            new_user
        )

    def login_user(
        self,
        db: Session,
        email: str,
        password: str
    ):

        user = user_repository.get_by_email(
            db,
            email
        )

        if not user:
            raise ValueError("Invalid email or password")

        if not verify_password(
            password,
            user.password_hash
        ):
            raise ValueError("Invalid email or password")

        token = create_access_token(
            {
                "sub": user.email
            }
        )

        return {
            "access_token": token,
            "token_type": "bearer"
        }


auth_service = AuthService()