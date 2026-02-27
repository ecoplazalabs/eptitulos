from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # Database
    database_url: str = (
        "postgresql+asyncpg://eptitulos:eptitulos_dev_2026@localhost:5432/eptitulos"
    )

    # JWT
    jwt_secret_key: str = "change-this-secret-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expiration_minutes: int = 1440  # 24 hours

    # Storage
    storage_path: str = "./storage"

    # n8n
    n8n_webhook_url: str
    n8n_api_key: str

    # App
    app_env: str = "development"
    app_version: str = "1.0.0"
    cors_origins: str = "http://localhost:5173"

    # Server
    host: str = "0.0.0.0"
    port: int = 8000

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",")]

    @property
    def is_production(self) -> bool:
        return self.app_env == "production"


settings = Settings()
