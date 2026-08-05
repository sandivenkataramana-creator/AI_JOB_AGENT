from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.auth.dependencies import get_current_user
from app.models.user import User
from fastapi.security import OAuth2PasswordRequestForm

from app.database.database import get_db
from app.schemas.user_schema import (
    UserRegister,
    UserResponse,
    TokenResponse,
)
from app.services.auth_service import auth_service

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def register(
    user: UserRegister,
    db: Session = Depends(get_db),
):
    try:
        return auth_service.register_user(db, user)
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e),
        )


@router.post(
    "/login",
    response_model=TokenResponse,
)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    try:
        return auth_service.login_user(
            db=db,
            email=form_data.username,
            password=form_data.password,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
        )

@router.get(
    "/me",
    response_model=UserResponse,
)
def current_user(
    user: User = Depends(get_current_user),
):
    return user