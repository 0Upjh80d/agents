from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()  # type: ignore
