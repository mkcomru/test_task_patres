from typing import Optional
from pydantic import field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str

    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    PROJECT_NAME: str = "Library API"
    DEBUG: bool = False
    API_V1_STR: str = "/api/v1"
    
    @field_validator("DATABASE_URL", mode="before")
    def validate_database_url(cls, v: Optional[str]) -> str:
        if not v:
            raise ValueError("DATABASE_URL должен быть указан")
        return v
        
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings() 