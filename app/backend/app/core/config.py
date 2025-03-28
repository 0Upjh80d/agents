from pydantic_settings import BaseSettings

# TODO: Store in Azure Key Vault


class Settings(BaseSettings):
    secret_key: str
    algorithm: str
    access_token_expire_minutes: int = 60
    refresh_token_expire_days: int = 2

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()  # type: ignore
