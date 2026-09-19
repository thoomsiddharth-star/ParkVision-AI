from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List, Union
import os

class Settings(BaseSettings):
    APP_NAME: str = "ParkVision AI Backend"
    DEBUG: bool = True
    AI_MODE: str = "demo"  # "demo" or "yolo"
    DATABASE_URL: str = "sqlite:///./parkvision.db"
    ADMIN_EMAIL: str = "admin@parkvision.ai"
    ADMIN_PASSWORD: str = "theasp@1234"
    JWT_SECRET: str = "parkvision-production-secret-key-hackathon-2026"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:3000,http://localhost:8000,http://127.0.0.1:5173,http://127.0.0.1:8000"
    SIMULATION_INTERVAL_SECONDS: float = 4.0
    GOOGLE_MAPS_API_KEY: str = ""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def cors_origins_list(self) -> List[str]:
        if isinstance(self.CORS_ORIGINS, list):
            return self.CORS_ORIGINS
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]

settings = Settings()
