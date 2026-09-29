from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    OPENAI_API_KEY: str = "sk-test-key"
    PYANNOTE_AUTH_TOKEN: str = "hf-test-token"
    DATABASE_URL: str = "sqlite:///./meat_lab.db"
    SMTP_HOST: str = "smtp.example.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = "your_email@example.com"
    SMTP_PASSWORD: str = "your_email_password"
    PRODUCT_MANAGER_EMAIL: str = "pm@meatlab.com"

    class Config:
        env_file = ".env"


settings = Settings()
