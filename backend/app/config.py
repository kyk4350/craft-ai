from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # 프로젝트 기본 정보
    PROJECT_NAME: str = "ContentCraft AI"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"

    # 환경 설정
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    # API Keys
    GEMINI_API_KEY: Optional[str] = None
    REPLICATE_API_TOKEN: Optional[str] = None
    STABILITY_API_KEY: Optional[str] = None
    VOYAGE_AI_API_KEY: Optional[str] = None

    # AI 모델 설정
    IMAGE_PROVIDER: str = "mock"  # mock, stability, nanobanana
    GEMINI_MODEL: str = "gemini-2.5-flash"  # gemini-2.5-flash, gemini-2.5-pro

    # 데이터베이스
    DATABASE_URL: Optional[str] = None

    # Redis
    REDIS_URL: Optional[str] = None

    # Qdrant Vector DB
    QDRANT_URL: Optional[str] = None
    QDRANT_API_KEY: Optional[str] = None

    # CORS
    BACKEND_CORS_ORIGINS: list = ["http://localhost:3000", "http://localhost:5173"]

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
