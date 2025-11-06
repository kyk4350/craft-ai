"""
사용자 인증 API 엔드포인트 (회원가입, 로그인)
"""

from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr, validator
from typing import Dict, Any, Optional
import re
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests

from app.models.base import get_db
from app.models.user import User
from app.utils.auth import (
    get_password_hash,
    verify_password,
    create_access_token
)
from app.config import settings

router = APIRouter(prefix="/api/auth", tags=["auth"])


# === Pydantic Schemas ===

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    name: str

    @validator('password')
    def validate_password(cls, v):
        """비밀번호 검증: 최소 8자, 영문+숫자 포함"""
        if len(v) < 8:
            raise ValueError('비밀번호는 최소 8자 이상이어야 합니다')

        if not re.search(r'[A-Za-z]', v):
            raise ValueError('비밀번호는 영문을 포함해야 합니다')

        if not re.search(r'\d', v):
            raise ValueError('비밀번호는 숫자를 포함해야 합니다')

        return v

    @validator('name')
    def validate_name(cls, v):
        """이름 검증: 2-50자"""
        if len(v) < 2 or len(v) > 50:
            raise ValueError('이름은 2-50자 사이여야 합니다')
        return v


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: Dict[str, Any]


class RegisterResponse(BaseModel):
    success: bool
    message: str
    user: Dict[str, Any]


# === API Endpoints ===

@router.post(
    "/register",
    response_model=RegisterResponse,
    summary="회원가입",
    description="이메일, 비밀번호, 이름으로 새 사용자를 등록합니다."
)
def register(request: RegisterRequest, db: Session = Depends(get_db)):
    """
    회원가입

    - 이메일 중복 체크
    - 비밀번호 해싱 (bcrypt)
    - 사용자 생성
    """
    # 이메일 중복 체크
    existing_user = db.query(User).filter(User.email == request.email).first()
    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="이미 등록된 이메일입니다"
        )

    # 비밀번호 해싱
    hashed_password = get_password_hash(request.password)

    # 사용자 생성
    user = User(
        email=request.email,
        hashed_password=hashed_password,
        name=request.name,
        is_active=True
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return RegisterResponse(
        success=True,
        message="회원가입이 완료되었습니다",
        user={
            "id": user.id,
            "email": user.email,
            "name": user.name,
            "created_at": user.created_at.isoformat()
        }
    )


@router.post(
    "/login",
    response_model=LoginResponse,
    summary="로그인",
    description="이메일과 비밀번호로 로그인하고 JWT 토큰을 받습니다."
)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    로그인

    - 이메일(username)과 비밀번호로 인증
    - JWT 액세스 토큰 발급 (7일 유효)
    - 사용자 정보 반환
    """
    # 사용자 조회
    user = db.query(User).filter(User.email == form_data.username).first()

    if not user:
        raise HTTPException(
            status_code=401,
            detail="이메일 또는 비밀번호가 올바르지 않습니다"
        )

    # 비밀번호 검증
    if not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=401,
            detail="이메일 또는 비밀번호가 올바르지 않습니다"
        )

    # 활성 사용자 체크
    if not user.is_active:
        raise HTTPException(
            status_code=403,
            detail="비활성화된 사용자입니다"
        )

    # JWT 토큰 생성
    access_token = create_access_token(data={"sub": str(user.id)})

    return LoginResponse(
        access_token=access_token,
        token_type="bearer",
        user={
            "id": user.id,
            "email": user.email,
            "name": user.name,
            "created_at": user.created_at.isoformat()
        }
    )


# === Google OAuth ===

class GoogleTokenRequest(BaseModel):
    """Google OAuth ID 토큰 요청"""
    token: str


@router.post(
    "/google",
    response_model=LoginResponse,
    summary="Google 로그인",
    description="Google OAuth ID 토큰으로 로그인합니다."
)
def google_login(
    request: GoogleTokenRequest,
    db: Session = Depends(get_db)
):
    """
    Google OAuth 로그인

    - Google ID 토큰 검증
    - 기존 사용자면 로그인, 신규면 자동 회원가입
    - JWT 액세스 토큰 발급
    """
    try:
        # Google ID 토큰 검증
        if not settings.GOOGLE_CLIENT_ID:
            raise HTTPException(
                status_code=500,
                detail="Google OAuth가 설정되지 않았습니다"
            )

        idinfo = id_token.verify_oauth2_token(
            request.token,
            google_requests.Request(),
            settings.GOOGLE_CLIENT_ID
        )

        # Google 계정 정보 추출
        google_id = idinfo['sub']
        email = idinfo.get('email')
        name = idinfo.get('name', email.split('@')[0])

        if not email:
            raise HTTPException(
                status_code=400,
                detail="Google 계정에서 이메일을 가져올 수 없습니다"
            )

        # 기존 사용자 확인 (google_id 또는 email로)
        user = db.query(User).filter(
            (User.google_id == google_id) | (User.email == email)
        ).first()

        if user:
            # 기존 사용자 - google_id 업데이트 (email로 가입했던 경우)
            if not user.google_id:
                user.google_id = google_id
                db.commit()
        else:
            # 신규 사용자 - 자동 회원가입
            user = User(
                email=email,
                name=name,
                google_id=google_id,
                hashed_password=None,  # Google 로그인은 비밀번호 없음
                is_active=True
            )
            db.add(user)
            db.commit()
            db.refresh(user)

        # JWT 토큰 생성
        access_token = create_access_token(data={"sub": str(user.id)})

        return LoginResponse(
            access_token=access_token,
            token_type="bearer",
            user={
                "id": user.id,
                "email": user.email,
                "name": user.name,
                "created_at": user.created_at.isoformat()
            }
        )

    except ValueError as e:
        # 토큰 검증 실패
        raise HTTPException(
            status_code=401,
            detail=f"유효하지 않은 Google 토큰입니다: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Google 로그인 중 오류가 발생했습니다: {str(e)}"
        )
