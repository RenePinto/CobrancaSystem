from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    username: str = Field(..., examples=["admin"])
    password: str = Field(..., examples=["secret"])
    totp_code: str | None = Field(default=None, examples=["123456"])


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TwoFactorSetupResponse(BaseModel):
    secret: str
    otpauth_url: str


class TwoFactorVerifyRequest(BaseModel):
    totp_code: str
