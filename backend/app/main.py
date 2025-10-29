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
from app.api import segmentation, content, content_generation

app.include_router(segmentation.router)
app.include_router(content.router)
app.include_router(content_generation.router)

# TODO: 추후 추가 예정
# from app.api import analysis
# app.include_router(analysis.router)
