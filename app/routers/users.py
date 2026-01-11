from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import require_role
from app.schemas.user import UserCreate, UserResponse
from app.services import auth_service

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("", response_model=UserResponse)
def create_user(
    payload: UserCreate,
    db: Session = Depends(get_db),
    _admin=Depends(require_role("admin")),
):
    try:
        user = auth_service.create_user(
            db,
            username=payload.username,
            full_name=payload.full_name,
            role=payload.role,
            password=payload.password,
        )
        return user
    except auth_service.AuthError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
