import os
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Database Local (Financeiro)
    DB_SERVER: str
    DB_PORT: int = 1433
    DB_NAME: str
    DB_USER: str
    DB_PASSWORD: str

    # Database Senior (Sapiens) - Leitura
    SENIOR_DB_SERVER: str
    SENIOR_DB_PORT: int = 1433
    SENIOR_DB_NAME: str
    SENIOR_DB_USER: str
    SENIOR_DB_PASSWORD: str

    # API
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    API_RELOAD: bool = True

    # CORS
    CORS_ORIGINS: list[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://localhost:8080",
        "http://10.50.3.3:8080",
        "http://localhost:8081",
        "http://10.50.3.3:8081",
        "http://10.212.135.208:8000",
        "https://financeiro.serviseletronica.com.br",
        "https://financeiro.serviseletronica.com.br:58769"
    ]

    # Timezone
    TIMEZONE: str = "America/Fortaleza"

    # OpenAI
    OPENAI_API_KEY: str

    # Autenticação JWT
    JWT_SECRET_KEY: str = "change-this-secret-key-in-production-use-a-strong-random-value"

    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"  # Ignora variáveis extras do .env


settings = Settings()
