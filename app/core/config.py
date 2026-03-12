from functools import lru_cache
from pathlib import Path

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).parent.parent.parent


class JWTAuthSettings(BaseModel):
    private_key_path: Path = PROJECT_ROOT / "certs" / "jwt-private.pem"
    public_key_path: Path = PROJECT_ROOT / "certs" / "jwt-public.pem"

    algorithm: str = "RS256"

    access_token_expire_minutes: int = 0


class DatabaseSettings(BaseModel):
    host: str = "localhost"
    port: str = "5432"
    name: str = "postgres"
    user: str = "postgres"
    password: str = "password"

    @property
    def url(self) -> str:
        return f"postgresql+asyncpg://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}"


class APISettings(BaseModel):
    host: str = "0.0.0.0"
    port: int = 8000


class Settings(BaseSettings):
    """
    Настройки приложения
    """

    database: DatabaseSettings = Field(default_factory=DatabaseSettings)
    jwt: JWTAuthSettings = Field(default_factory=JWTAuthSettings)

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
        env_nested_delimiter="__",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
