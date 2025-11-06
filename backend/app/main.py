from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv
from pathlib import Path
import os

load_dotenv()

app = FastAPI(
    title="ContentCraft AI API",
    description="AI-powered marketing content generation platform",
    version="1.0.0"
)

# Static files 설정 (이미지 서빙)
storage_dir = Path(__file__).parent.parent / "storage" / "images"
storage_dir.mkdir(parents=True, exist_ok=True)
app.mount("/static/images", StaticFiles(directory=str(storage_dir)), name="images")

# Static files 설정 (업로드된 제품 이미지 서빙)
uploads_dir = Path(__file__).parent.parent / "static" / "uploads"
uploads_dir.mkdir(parents=True, exist_ok=True)
app.mount("/static/uploads", StaticFiles(directory=str(uploads_dir)), name="uploads")

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 개발 환경, 프로덕션에서는 특정 도메인으로 제한
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {
        "message": "ContentCraft AI API",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# API 라우터 등록
from app.api import content, content_generation, performance, analytics, contents, auth, projects, chat, upload

app.include_router(auth.router)
app.include_router(projects.router)
app.include_router(chat.router)
app.include_router(upload.router)
app.include_router(content.router)
app.include_router(content_generation.router)
app.include_router(performance.router)
app.include_router(analytics.router)
app.include_router(contents.router)
