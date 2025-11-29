from pydantic import SecretStr
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # LLM API
    API_KEY: str = "io-v2-eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJvd25lciI6ImUzNDRlZjExLTQ0NzItNDFjMS1iOTA5LWQyMjlkMzZkN2Q0MCIsImV4cCI6NDkxNzM2MTUyOH0.a31bOPKDAjLEGmqCJtCEqOq8m4sEo35vrP7bVAN23pnzSi0UF8_jiS4AYfAT5lh9YrGflqvRMmVr27AwH-Yr1w"
    AI_MODEL: str = "mistralai/Mistral-Nemo-Instruct-2407"

    # CORS и общие настройки
    ORIGINS: str = "*"
    ROOT_PATH: str = ""
    ENV: str = "DEV"
    LOG_LEVEL: str = "DEBUG"

    # PostgreSQL
    POSTGRES_SCHEMA: str = "ssu_bot"
    POSTGRES_HOST: str = "db"
    POSTGRES_DB: str = "postgres"
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: SecretStr = "user"
    POSTGRES_PASSWORD: SecretStr = "password"
    POSTGRES_RECONNECT_INTERVAL_SEC: int = 1

    @property
    def postgres_url(self) -> str:
        creds = f"{self.POSTGRES_USER.get_secret_value()}:{self.POSTGRES_PASSWORD.get_secret_value()}"
        return f"postgresql+asyncpg://{creds}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
