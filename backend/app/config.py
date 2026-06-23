from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="TRAINER_")

    database_url: str = "sqlite:///./data/trainer.db"
    default_user_id: int = 1
    code_timeout_seconds: float = 2.0
    auth_enabled: bool = True
    admin_email: str = "admin@local"
    admin_password: str = "dev"
    jwt_secret: str = "dev-insecure-change-me"
    jwt_expire_hours: int = 24
    cookie_name: str = "trainer_token"
    cookie_secure: bool = False
    cors_origins: str = "https://python-simulator.ai-smirnov.ru"
    ai_enabled: bool = False
    openai_api_key: str = ""
    ai_model: str = "meta-llama/llama-3.3-70b-instruct:free"
    ai_base_url: str = "https://openrouter.ai/api/v1"
    ai_http_referer: str = "https://python-simulator.ai-smirnov.ru"
    ai_app_title: str = "Python Refresh Trainer"
    ai_timeout_seconds: float = 45.0

    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


settings = Settings()
