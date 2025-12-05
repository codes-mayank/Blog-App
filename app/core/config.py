from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "mysql+pymysql://root:root@localhost/test"


    # App Settings
    APP_NAME: str = "FastAPI App Backend"
    DEBUG: bool = True

    SECRET_KEY: str = 'secret-key'
    ALGORITHM: str = 'HS256'
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    ACCESS_TOKEN_COOKIE_NAME: str = "access_token"

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings() 