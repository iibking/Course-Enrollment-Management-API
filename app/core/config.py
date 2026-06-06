from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # General 
    PROJECT_NAME: str = "Course Enrollment API"
    ENVIRONMENT: str = "DEBUG"                 # DEBUG | STAGING | PRODUCTION

    # Auth 
    SECRET_KEY: str                           # required — no insecure default
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Database
    DATABASE_URL: str = ""                     # sync  — used by Alembic
    DATABASE_URL_ASYNC: str = ""               # async — used by the app

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @model_validator(mode="after")
    def _derive_database_urls(self):
        """
        Hosts like Render provide a single Postgres URL. Normalize it and fill
        in whichever of the sync/async URLs wasn't supplied explicitly:
          - "postgres://"   -> "postgresql://"            (SQLAlchemy needs this)
          - sync  -> async  by inserting the asyncpg driver
          - async -> sync   by removing the asyncpg driver
        """
        sync = self.DATABASE_URL
        if sync.startswith("postgres://"):
            sync = sync.replace("postgres://", "postgresql://", 1)
            self.DATABASE_URL = sync

        if not self.DATABASE_URL_ASYNC and sync:
            self.DATABASE_URL_ASYNC = (
                sync.replace("postgresql://", "postgresql+asyncpg://", 1)
                if sync.startswith("postgresql://") else sync
            )

        if not self.DATABASE_URL and self.DATABASE_URL_ASYNC:
            self.DATABASE_URL = self.DATABASE_URL_ASYNC.replace("+asyncpg", "")

        return self

    @property
    def is_debug(self) -> bool:
        """True in local development — used to toggle SQL echo."""
        return self.ENVIRONMENT == "DEBUG"

    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT == "PRODUCTION"


settings = Settings()