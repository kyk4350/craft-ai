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

    # 인증
    SECRET_KEY: str = "FMkksDAZiBOx2bXeYyb0IzyCP92HGYIes4Q2PwrMGA4"  # 프로덕션에서는 환경변수로 설정

    # API Keys
    GEMINI_API_KEY: Optional[str] = None
    REPLICATE_API_TOKEN: Optional[str] = None
    STABILITY_API_KEY: Optional[str] = None
    VOYAGE_AI_API_KEY: Optional[str] = None
    IDEOGRAM_API_KEY: Optional[str] = None

    # AI 모델 설정
    IMAGE_PROVIDER: str = "replicate"  # replicate (SDXL, Ideogram)
    IMAGE_MODE: str = "development"  # development (SDXL), production (Ideogram v3 Turbo)
    GEMINI_MODEL: str = "gemini-2.5-flash"  # gemini-2.5-flash, gemini-2.5-pro

    # 데이터베이스
    DATABASE_URL: Optional[str] = None

    # Redis
    REDIS_URL: Optional[str] = None

    # Qdrant Vector DB
    QDRANT_URL: Optional[str] = None
    QDRANT_API_KEY: Optional[str] = None

    # Google OAuth
    GOOGLE_CLIENT_ID: Optional[str] = None
    GOOGLE_CLIENT_SECRET: Optional[str] = None
    GOOGLE_REDIRECT_URI: str = "http://localhost:8000/api/auth/google/callback"

    # CORS
    BACKEND_CORS_ORIGINS: list = ["http://localhost:3000", "http://localhost:5173"]

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
