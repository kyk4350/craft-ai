"""
제품 이미지 업로드 API
사용자가 업로드한 제품 이미지를 저장하고 관리
"""

from fastapi import APIRouter, HTTPException, UploadFile, File, Depends
from fastapi.responses import JSONResponse
from typing import Optional
import logging
import os
import shutil
from datetime import datetime
from pathlib import Path
import uuid

from app.models.user import User
from app.utils.auth import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/upload", tags=["upload"])

# 업로드 디렉토리 설정
UPLOAD_DIR = Path(__file__).parent.parent.parent / "static" / "uploads" / "products"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# 허용된 이미지 확장자
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}

# 최대 파일 크기 (10MB)
MAX_FILE_SIZE = 10 * 1024 * 1024


def validate_image_file(file: UploadFile) -> None:
    """
    이미지 파일 유효성 검증

    Args:
        file: 업로드된 파일

    Raises:
        HTTPException: 파일이 유효하지 않을 때
    """
    # 파일명 확인
    if not file.filename:
        raise HTTPException(status_code=400, detail="파일명이 없습니다")

    # 확장자 확인
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"허용되지 않는 파일 형식입니다. 허용 형식: {', '.join(ALLOWED_EXTENSIONS)}"
        )


@router.post("/product-image")
async def upload_product_image(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    """
    제품 이미지 업로드

    **동작:**
    1. 이미지 파일 유효성 검증 (형식, 크기)
    2. 고유한 파일명으로 저장
    3. 저장된 파일 경로 반환

    **Returns:**
    - file_path: 서버에 저장된 파일 경로
    - public_url: 클라이언트에서 접근 가능한 URL
    - filename: 원본 파일명
    """
    try:
        logger.info(f"제품 이미지 업로드 시작: {file.filename}")

        # 파일 유효성 검증
        validate_image_file(file)

        # 파일 크기 확인
        file.file.seek(0, 2)  # 파일 끝으로 이동
        file_size = file.file.tell()
        file.file.seek(0)  # 파일 시작으로 되돌림

        if file_size > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=400,
                detail=f"파일 크기가 너무 큽니다. 최대 크기: {MAX_FILE_SIZE / 1024 / 1024}MB"
            )

        logger.info(f"파일 크기: {file_size / 1024:.2f} KB")

        # 고유한 파일명 생성 (UUID + 원본 확장자)
        file_ext = Path(file.filename).suffix.lower()
        unique_filename = f"{uuid.uuid4()}{file_ext}"

        # 사용자별 디렉토리 생성 (옵션)
        user_dir = UPLOAD_DIR / str(current_user.id)
        user_dir.mkdir(parents=True, exist_ok=True)

        # 파일 저장
        file_path = user_dir / unique_filename

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        logger.info(f"✓ 제품 이미지 저장 완료: {file_path}")

        # 공개 URL 생성
        public_url = f"/static/uploads/products/{current_user.id}/{unique_filename}"

        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "data": {
                    "file_path": str(file_path),
                    "public_url": public_url,
                    "filename": file.filename,
                    "size": file_size
                },
                "message": "제품 이미지 업로드 완료"
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"제품 이미지 업로드 실패: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"이미지 업로드 중 오류가 발생했습니다: {str(e)}"
        )


@router.delete("/product-image")
async def delete_product_image(
    file_path: str,
    current_user: User = Depends(get_current_user)
):
    """
    제품 이미지 삭제

    **Args:**
    - file_path: 삭제할 파일 경로

    **Returns:**
    - success: 성공 여부
    - message: 응답 메시지
    """
    try:
        logger.info(f"제품 이미지 삭제 시작: {file_path}")

        # 파일 경로 검증 (사용자 디렉토리 내의 파일만 삭제 가능)
        file_path_obj = Path(file_path)

        if not file_path_obj.exists():
            raise HTTPException(status_code=404, detail="파일을 찾을 수 없습니다")

        # 사용자 소유 파일인지 확인
        user_dir = UPLOAD_DIR / str(current_user.id)
        if not str(file_path_obj).startswith(str(user_dir)):
            raise HTTPException(status_code=403, detail="해당 파일에 대한 권한이 없습니다")

        # 파일 삭제
        file_path_obj.unlink()

        logger.info(f"✓ 제품 이미지 삭제 완료: {file_path}")

        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "message": "제품 이미지 삭제 완료"
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"제품 이미지 삭제 실패: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"이미지 삭제 중 오류가 발생했습니다: {str(e)}"
        )
