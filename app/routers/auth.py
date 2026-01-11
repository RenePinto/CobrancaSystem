from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.schemas.auth import (
    LoginRequest,
    TokenResponse,
    TwoFactorSetupResponse,
    TwoFactorVerifyRequest,
)
from app.services import auth_service

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    try:
        token = auth_service.authenticate_user(
            db, payload.username, payload.password, payload.totp_code
        )
        return TokenResponse(access_token=token)
    except auth_service.AuthError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc


@router.post("/setup-2fa", response_model=TwoFactorSetupResponse)
def setup_2fa(current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    secret, otpauth_url = auth_service.setup_2fa(db, current_user)
    return TwoFactorSetupResponse(secret=secret, otpauth_url=otpauth_url)


@router.post("/verify-2fa")
def verify_2fa(
    payload: TwoFactorVerifyRequest,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        auth_service.verify_2fa(db, current_user, payload.totp_code)
        return {"status": "2FA habilitado"}
    except auth_service.AuthError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
