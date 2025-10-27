from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

load_dotenv()

app = FastAPI(
    title="ContentCraft AI API",
    description="AI-powered marketing content generation platform",
    version="1.0.0"
)

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

# API 라우터는 추가 예정
# from app.api import segmentation, generation, analysis
# app.include_router(segmentation.router, prefix="/api/segmentation", tags=["segmentation"])
# app.include_router(generation.router, prefix="/api/generation", tags=["generation"])
# app.include_router(analysis.router, prefix="/api/analysis", tags=["analysis"])
