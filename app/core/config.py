from functools import lru_cache
from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "CobrancaSystem"
    environment: str = "development"
    database_url: str = Field(
        default="postgresql+psycopg2://cobranca:cobranca@db:5432/cobranca",
        env="DATABASE_URL",
    )
    jwt_secret_key: str = Field(default="change-me", env="JWT_SECRET_KEY")
    jwt_algorithm: str = "HS256"
    jwt_expires_minutes: int = 60 * 8

    class Config:
        env_file = ".env"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
