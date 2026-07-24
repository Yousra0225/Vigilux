import warnings
from pathlib import Path

from pydantic import AnyHttpUrl, ValidationInfo, field_validator
from pydantic_settings import BaseSettings

# Get the backend directory path and locate .env in parent (root) directory
# config.py is at: backend/app/core/config.py
# Go up 4 levels: core -> app -> backend -> root
BACKEND_DIR = Path(__file__).resolve().parent.parent.parent.parent
ENV_FILE = BACKEND_DIR / ".env"

class Settings(BaseSettings):
    # Project Info
    PROJECT_NAME: str = "Vigilux"
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: str = "development"
    BACKEND_CORS_ORIGINS: list[AnyHttpUrl] = []

    DEBUG: bool = True

    # Database Configuration
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_USER: str = "vigilux_user"
    POSTGRES_PASSWORD: str = "vigilux_password"
    POSTGRES_DB: str = "vigilux"
    DATABASE_URL: str | None = None

    # Security Configuration
    # IMPORTANT: SECRET_KEY must be set in .env file!
    # Generate with: openssl rand -hex 32
    SECRET_KEY: str = "INSECURE_DEFAULT_CHANGE_ME"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Redis / Celery Configuration
    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_URL: str | None = None

    # Apify Configuration (Web Scraping)
    APIFY_API_TOKEN: str = ""

    # Google Gemini AI Configuration
    GEMINI_API_KEY: str = ""

    # SendGrid Configuration (Email Notifications)
    SENDGRID_API_KEY: str = ""
    SENDGRID_FROM_EMAIL: str = "noreply@vigilux.com"
    SENDGRID_FROM_NAME: str = "Vigilux"

    # Twilio Configuration (SMS Notifications)
    TWILIO_ACCOUNT_SID: str = ""
    TWILIO_AUTH_TOKEN: str = ""
    TWILIO_PHONE_NUMBER: str = ""

    # Slack Configuration (Slack Notifications)
    SLACK_WEBHOOK_URL: str = ""

    # Monitoring & Logging
    SENTRY_DSN: str = ""
    LOG_LEVEL: str = "INFO"

    @field_validator("SECRET_KEY", mode="after")
    @classmethod
    def validate_secret_key(cls, v: str, info: ValidationInfo) -> str:
        """Validate that SECRET_KEY has been changed from default value."""
        if v == "INSECURE_DEFAULT_CHANGE_ME":
            # Get environment from info
            values = info.data if hasattr(info, 'data') else {}
            env = values.get('ENVIRONMENT', 'development')

            if env == "production":
                raise ValueError(
                    "SECRET_KEY must be set in production! "
                    "Generate one with: openssl rand -hex 32"
                )
            else:
                warnings.warn(
                    "WARNING: Using default SECRET_KEY! This is insecure. "
                    "Generate a secure key with: openssl rand -hex 32",
                    UserWarning
                )
        return v

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: str | list[str]) -> list[str] | str:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        return []

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def assemble_db_connection(cls, v: str | None, info: ValidationInfo) -> str:
        if isinstance(v, str):
            return v
        # Get values from info for Pydantic v2
        values = info.data if hasattr(info, 'data') else {}
        # Manually construct to avoid Pydantic v2 complexity for now
        return f"postgresql://{values.get('POSTGRES_USER')}:{values.get('POSTGRES_PASSWORD')}@{values.get('POSTGRES_SERVER')}/{values.get('POSTGRES_DB')}"

    @field_validator("REDIS_URL", mode="before")
    @classmethod
    def assemble_redis_connection(cls, v: str | None, info: ValidationInfo) -> str:
        if isinstance(v, str):
            return v
        # Get values from info for Pydantic v2
        values = info.data if hasattr(info, 'data') else {}
        return f"redis://{values.get('REDIS_HOST')}:{values.get('REDIS_PORT')}/{values.get('REDIS_DB')}"

    model_config = {
        "case_sensitive": True,
        "env_file": str(ENV_FILE),
        "env_file_encoding": "utf-8",
        "extra": "ignore"  # Ignore extra fields like frontend vars (NEXT_PUBLIC_*)
    }

settings = Settings()
