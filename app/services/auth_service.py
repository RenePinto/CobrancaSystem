import pyotp
from sqlalchemy.orm import Session

from app.core.security import create_access_token, hash_password, verify_password
from app.models import User
from app.repositories import user_repository


class AuthError(Exception):
    pass


def authenticate_user(db: Session, username: str, password: str, totp_code: str | None) -> str:
    user = user_repository.get_by_username(db, username)
    if not user or not verify_password(password, user.password_hash):
        raise AuthError("Credenciais inválidas.")
    if user.is_2fa_enabled:
        if not totp_code:
            raise AuthError("Código TOTP obrigatório.")
        totp = pyotp.TOTP(user.totp_secret)
        if not totp.verify(totp_code):
            raise AuthError("Código TOTP inválido.")
    return create_access_token(subject=str(user.id), role=user.role)


def create_user(db: Session, username: str, full_name: str, role: str, password: str) -> User:
    existing = user_repository.get_by_username(db, username)
    if existing:
        raise AuthError("Usuário já existe.")
    user = User(
        username=username,
        full_name=full_name,
        role=role,
        password_hash=hash_password(password),
        is_2fa_enabled=False,
    )
    return user_repository.create(db, user)


def setup_2fa(db: Session, user: User) -> tuple[str, str]:
    secret = pyotp.random_base32()
    totp = pyotp.TOTP(secret)
    user.totp_secret = secret
    user.is_2fa_enabled = False
    db.add(user)
    db.commit()
    db.refresh(user)
    otpauth_url = totp.provisioning_uri(name=user.username, issuer_name="CobrancaSystem")
    return secret, otpauth_url


def verify_2fa(db: Session, user: User, totp_code: str) -> User:
    if not user.totp_secret:
        raise AuthError("2FA não configurado.")
    totp = pyotp.TOTP(user.totp_secret)
    if not totp.verify(totp_code):
        raise AuthError("Código TOTP inválido.")
    user.is_2fa_enabled = True
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
