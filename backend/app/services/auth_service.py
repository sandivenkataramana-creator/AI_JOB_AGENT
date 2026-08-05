from sqlalchemy.orm import Session

from app.auth.hashing import hash_password
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


auth_service = AuthService()