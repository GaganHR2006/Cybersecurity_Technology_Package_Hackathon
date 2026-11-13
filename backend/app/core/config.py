from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    DATABASE_URL: str = "sqlite:///./data/cyberwatch.db"
    SECRET_KEY: str = "dev-secret-key-change-in-production"
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:5173"]
    CORRELATION_WINDOW_MINUTES: int = 15
    RISK_WEIGHT_SEVERITY: float = 0.35
    RISK_WEIGHT_ASSET: float = 0.25
    RISK_WEIGHT_CHAIN: float = 0.25
    RISK_WEIGHT_CONTEXT: float = 0.15
    MIN_ALERTS_FOR_INCIDENT: int = 2

settings = Settings()
