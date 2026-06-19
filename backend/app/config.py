from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="TRAINER_")

    database_url: str = "sqlite:///./data/trainer.db"
    default_user_id: int = 1
    code_timeout_seconds: float = 2.0


settings = Settings()
