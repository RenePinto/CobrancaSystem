from datetime import datetime
from pydantic import BaseModel, Field


class UserCreate(BaseModel):
    username: str = Field(..., examples=["maria"])
    full_name: str = Field(..., examples=["Maria Silva"])
    role: str = Field(..., examples=["admin"])
    password: str = Field(..., examples=["secret123"])


class UserResponse(BaseModel):
    id: int
    username: str
    full_name: str
    role: str
    is_2fa_enabled: bool
    created_at: datetime

    class Config:
        orm_mode = True
