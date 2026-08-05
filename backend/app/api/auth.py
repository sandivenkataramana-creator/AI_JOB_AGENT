from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.schemas.user_schema import UserRegister, UserResponse
from app.services.auth_service import auth_service

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED
)
def register(
    user: UserRegister,
    db: Session = Depends(get_db)
):
    try:
        return auth_service.register_user(
            db,
            user
        )
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )