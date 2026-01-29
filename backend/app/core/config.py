from typing import List, Union, Optional
from pydantic import AnyHttpUrl, validator, PostgresDsn
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Vigilux"
    API_V1_STR: str = "/api/v1"
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []
    
    DEBUG: bool = True
    
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_USER: str = "vigilux_user"
    POSTGRES_PASSWORD: str = "vigilux_password"
    POSTGRES_DB: str = "vigilux"
    DATABASE_URL: Optional[str] = None

    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    @validator("DATABASE_URL", pre=True)
    def assemble_db_connection(cls, v: Optional[str], values: dict[str, any]) -> any:
        if isinstance(v, str):
            return v
        # Manually construct to avoid Pydantic v2 complexity for now
        return f"postgresql://{values.get('POSTGRES_USER')}:{values.get('POSTGRES_PASSWORD')}@{values.get('POSTGRES_SERVER')}/{values.get('POSTGRES_DB')}"

    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings()
